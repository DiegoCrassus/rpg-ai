#!/usr/bin/env python3
"""CLI for SDLC learning loop — record, analyze, policy update."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
SCRIPTS = ROOT / ".sdlc" / "scripts"
if str(LEARNING) not in sys.path:
    sys.path.insert(0, str(LEARNING))

from event_store import (  # noqa: E402
    events_path,
    load_qa_metrics,
    record_task,
    status_text,
    tail,
)
from policy_memory import ensure_seed, hints_for_spawn, update_for_card  # noqa: E402
from policy_optimizer import analyze  # noqa: E402

GATE_PATH = ROOT / ".sdlc" / "memory" / "session-gate.json"
HANDOFF_PATH = ROOT / ".sdlc" / "memory" / "orchestrator-handoff.md"
LEDGER_PATH = ROOT / ".sdlc" / "manifest" / "executions.jsonl"


def _load_gate() -> dict:
    if not GATE_PATH.is_file():
        return {}
    try:
        data = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _save_gate(gate: dict) -> None:
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")


def _load_token_budget() -> dict:
    path = ROOT / ".sdlc" / "memory" / "token-budget.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _handoff_field(section: str, field: str) -> str:
    if not HANDOFF_PATH.is_file():
        return ""
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    pattern = rf"##\s*{re.escape(section)}\s*\n+.*?\|\s*\*\*{re.escape(field)}\*\*\s*\|\s*`?([^`|]+)`?"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _reviewer_verdict() -> str | None:
    previous = _handoff_field("Routing", "Previous agent").lower()
    if previous != "reviewer":
        return None
    validation = (HANDOFF_PATH.read_text(encoding="utf-8") if HANDOFF_PATH.is_file() else "").lower()
    if "escalate" in validation:
        return "ESCALATE"
    if "approve" in validation:
        return "APPROVE"
    return None


def _recent_gateway_block(card: str) -> bool:
    if not LEDGER_PATH.is_file():
        return False
    lines = [ln for ln in LEDGER_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for line in reversed(lines[-30:]):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event_type") != "gateway_block":
            continue
        if event.get("card") and str(event["card"]).upper() != card.upper():
            continue
        return True
    return False


def _detect_gateway_block(gate: dict, card: str, *, explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    meta = gate.get("meta") or {}
    if meta.get("last_gateway_block"):
        return True
    stage_complete = _handoff_field("Routing", "Stage complete").lower()
    if stage_complete == "no":
        return True
    return _recent_gateway_block(card)


def _ensure_qa_evidence(card: str, agent: str) -> None:
    if agent != "qa" or not card:
        return
    if load_qa_metrics(card):
        return
    script = SCRIPTS / "qa_evidence.py"
    if not script.is_file():
        return
    subprocess.run(
        [sys.executable, str(script), "write", "--card", card],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )


def cmd_record_from_session(args: argparse.Namespace) -> int:
    gate = _load_gate()
    if gate.get("gate_status") != "open":
        return 0
    card = gate.get("card") or ""
    if not card:
        return 0

    agent = args.agent or gate.get("last_agent") or "unknown"
    if args.agent:
        gate["last_agent"] = agent
        meta = dict(gate.get("meta") or {})
        meta["last_recorded_agent"] = agent
        gate["meta"] = meta
        _save_gate(gate)

    _ensure_qa_evidence(card, agent)

    qa = load_qa_metrics(card)
    tests = qa.get("tests") or {}
    doctor = qa.get("doctor") or {}
    budget = _load_token_budget()
    meta = gate.get("meta") or {}
    gateway_block = _detect_gateway_block(
        gate,
        card,
        explicit=args.gateway_block if args.gateway_block is not None else None,
    )
    rework_count = int(meta.get("rework_count") or 0)
    if gateway_block:
        rework_count += 1
        meta["rework_count"] = rework_count
        meta["last_gateway_block"] = False
        gate["meta"] = meta
        _save_gate(gate)

    reviewer_verdict = _reviewer_verdict() if agent == "reviewer" else None

    record_task(
        card=card,
        agent=agent,
        stage=gate.get("stage") or "",
        intent=gate.get("intent") or "",
        branch=gate.get("branch") or "",
        tokens_in=int(budget.get("session_input") or budget.get("input") or 0),
        tokens_out=int(budget.get("session_output") or budget.get("output") or 0),
        tests_pass=int(tests.get("passed") or 0) if tests else None,
        tests_fail=int(tests.get("failed") or 0) if tests else None,
        doctor_exit=int(doctor.get("exit_code")) if doctor else None,
        gateway_block=gateway_block,
        rework_count=rework_count,
        reviewer_verdict=reviewer_verdict,
        session_id=gate.get("opened_at") or "",
    )
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    print(status_text())
    path = events_path()
    if path.is_file():
        print("path_exists: yes")
    else:
        print("path_exists: no")
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    for e in tail(args.n):
        print(json.dumps(e.to_dict(), ensure_ascii=False))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    print(json.dumps(analyze(args.last), indent=2, ensure_ascii=False))
    return 0


def cmd_policy_update(args: argparse.Namespace) -> int:
    card = args.card or _load_gate().get("card") or ""
    if not card:
        print("ERROR: --card required", file=sys.stderr)
        return 1
    ensure_seed(ROOT)
    data = update_for_card(card, root=ROOT)
    print(f"OK: policy_memory updated — {len(data.get('rules') or [])} rules")
    return 0


def cmd_hints(args: argparse.Namespace) -> int:
    hints = hints_for_spawn(
        task_type=args.task_type,
        stage=args.stage,
        agent=args.agent,
        root=ROOT,
    )
    print(json.dumps(hints, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SDLC learning loop CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    rs = sub.add_parser("record-session", help="Record task event from gate + QA metrics")
    rs.add_argument("--agent", default="", help="Subagent that just finished")
    rs.add_argument(
        "--gateway-block",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Force gateway_block signal for reward",
    )

    sub.add_parser("status")
    t = sub.add_parser("tail")
    t.add_argument("-n", type=int, default=20)
    a = sub.add_parser("analyze")
    a.add_argument("--last", type=int, default=100)
    p = sub.add_parser("policy-update")
    p.add_argument("--card", default="")
    h = sub.add_parser("hints")
    h.add_argument("--task-type", default="feature")
    h.add_argument("--stage", default="implementation")
    h.add_argument("--agent", default="implementer")

    args = parser.parse_args(argv)
    handlers = {
        "record-session": cmd_record_from_session,
        "status": cmd_status,
        "tail": cmd_tail,
        "analyze": cmd_analyze,
        "policy-update": cmd_policy_update,
        "hints": cmd_hints,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
