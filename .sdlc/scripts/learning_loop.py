#!/usr/bin/env python3
"""CLI for SDLC learning loop — record, analyze, policy update."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
if str(LEARNING) not in sys.path:
    sys.path.insert(0, str(LEARNING))

from event_store import (  # noqa: E402
    load_qa_metrics,
    record_task,
    status_text,
    tail,
)
from policy_memory import hints_for_spawn, update_for_card  # noqa: E402
from policy_optimizer import analyze  # noqa: E402


def _load_gate() -> dict:
    path = ROOT / ".sdlc" / "memory" / "session-gate.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_token_budget() -> dict:
    path = ROOT / ".sdlc" / "memory" / "token-budget.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def cmd_record_from_session(_args: argparse.Namespace) -> int:
    gate = _load_gate()
    if gate.get("gate_status") != "open":
        return 0
    card = gate.get("card") or ""
    if not card:
        return 0
    agent = gate.get("last_agent") or "unknown"
    qa = load_qa_metrics(card)
    tests = qa.get("tests") or {}
    doctor = qa.get("doctor") or {}
    budget = _load_token_budget()
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
        session_id=gate.get("opened_at") or "",
    )
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    print(status_text())
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
    data = update_for_card(card)
    print(f"OK: policy_memory updated — {len(data.get('rules') or [])} rules")
    return 0


def cmd_hints(args: argparse.Namespace) -> int:
    hints = hints_for_spawn(
        task_type=args.task_type,
        stage=args.stage,
        agent=args.agent,
    )
    print(json.dumps(hints, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SDLC learning loop CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("record-session", help="Record task event from gate + QA metrics")
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
