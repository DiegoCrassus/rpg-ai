#!/usr/bin/env python3
"""Execution ledger — append-only SDLC run manifest (Harness v6 Layer 2)."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / ".sdlc" / "manifest" / "executions.jsonl"
MEMORY_DIR = ROOT / ".sdlc" / "memory"
SESSION_GATE = MEMORY_DIR / "session-gate.json"
HANDOFF_PATH = MEMORY_DIR / "orchestrator-handoff.md"
OBS_STATE = ROOT / ".sdlc_obs_state.json"
MAX_LEDGER_LINES = 500
SCHEMA_VERSION = 1


def repo_root() -> Path:
    return ROOT


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_session_gate() -> dict[str, Any]:
    if not SESSION_GATE.is_file():
        return {}
    try:
        data = json.loads(SESSION_GATE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def session_id(gate: dict[str, Any] | None = None) -> str:
    gate = gate or load_session_gate()
    meta = gate.get("meta") or {}
    if run_id := meta.get("session_id"):
        return str(run_id)
    if opened := gate.get("opened_at"):
        return str(opened)
    if OBS_STATE.is_file():
        try:
            obs = json.loads(OBS_STATE.read_text(encoding="utf-8"))
            if obs.get("run_id"):
                return str(obs["run_id"])
        except (OSError, json.JSONDecodeError):
            pass
    return str(uuid.uuid4())


def parse_handoff_fields() -> dict[str, str]:
    if not HANDOFF_PATH.is_file():
        return {}
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    fields: dict[str, str] = {}

    def _table_field(section: str, field: str) -> str:
        pattern = rf"##\s*{re.escape(section)}\s*\n+.*?\|\s*\*\*{re.escape(field)}\*\*\s*\|\s*`?([^`|]+)`?"
        match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    fields["next_agent"] = _table_field("Routing", "Next agent")
    fields["stage_complete"] = _table_field("Routing", "Stage complete")
    fields["previous_agent"] = _table_field("Routing", "Previous agent")
    fields["card"] = _table_field("Session", "Card")
    fields["branch"] = _table_field("Session", "Branch")
    fields["stage"] = _table_field("Session", "Stage")
    return fields


def compute_reward(
    event: str,
    outcome: dict[str, Any],
    *,
    prior_autofix_count: int = 0,
) -> float:
    reward = 1.0
    if event == "gateway_block":
        reward -= 0.3
    if event == "autofix_cycle":
        reward -= 0.2
    if outcome.get("evidence_verified") is False:
        reward -= 0.5
    if outcome.get("handoff_complete") is False:
        reward -= 0.3
    if event == "stage_complete" and outcome.get("stage_complete") == "yes":
        if prior_autofix_count == 0 and outcome.get("agent") == "qa":
            reward += 0.1
    return max(0.0, min(1.0, reward))


def read_lines(path: Path | None = None) -> list[str]:
    path = path or LEDGER_PATH
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_events(path: Path | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in read_lines(path):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except json.JSONDecodeError:
            continue
    return events


def prune_ledger(max_lines: int = MAX_LEDGER_LINES, path: Path | None = None) -> int:
    path = path or LEDGER_PATH
    lines = read_lines(path)
    if len(lines) <= max_lines:
        return 0
    kept = lines[-max_lines:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return len(lines) - max_lines


def append_event(
    event: dict[str, Any],
    *,
    root: Path | None = None,
    max_lines: int = MAX_LEDGER_LINES,
) -> Path:
    root = root or repo_root()
    path = root / ".sdlc" / "manifest" / "executions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {"v": SCHEMA_VERSION, "ts": _now_iso(), **event}
    if "session_id" not in record:
        record["session_id"] = session_id()

    if "reward" not in record:
        record["reward"] = compute_reward(
            str(record.get("event", "stage_complete")),
            record.get("outcome") or {},
        )

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    prune_ledger(max_lines, path)
    return path


def build_gateway_event(
    *,
    event_type: str,
    reason: str = "",
    details: list[str] | None = None,
    evidence_verified: bool | None = None,
    human_note: str = "",
) -> dict[str, Any]:
    gate = load_session_gate()
    handoff = parse_handoff_fields()
    card = handoff.get("card") or gate.get("card") or ""
    branch = handoff.get("branch") or gate.get("branch") or ""
    stage = handoff.get("stage") or gate.get("stage") or ""
    agent = handoff.get("previous_agent") or gate.get("last_agent") or ""

    prior = read_events()
    autofix_count = sum(
        1 for e in prior if e.get("card") == card and e.get("event") == "autofix_cycle"
    )

    outcome: dict[str, Any] = {
        "handoff_complete": event_type != "gateway_block",
        "stage_complete": handoff.get("stage_complete", ""),
        "agent": agent,
    }
    if evidence_verified is not None:
        outcome["evidence_verified"] = evidence_verified

    blockers = details or ([reason] if reason else [])
    record: dict[str, Any] = {
        "session_id": session_id(gate),
        "card": card,
        "branch": branch,
        "stage": stage,
        "agent": agent,
        "event": event_type,
        "outcome": outcome,
        "reward": compute_reward(
            event_type,
            outcome,
            prior_autofix_count=autofix_count,
        ),
        "blockers": blockers,
    }
    if human_note:
        record["human_note"] = human_note
    elif reason and event_type == "gateway_block":
        record["human_note"] = reason[:200]
    return record


def append_from_gateway(
    event_type: str,
    *,
    reason: str = "",
    details: list[str] | None = None,
    evidence_verified: bool | None = None,
) -> None:
    """Best-effort append; never raise to caller (hooks must stay safe)."""
    try:
        event = build_gateway_event(
            event_type=event_type,
            reason=reason,
            details=details,
            evidence_verified=evidence_verified,
        )
        append_event(event)
    except Exception:
        return


def events_for_card(card: str) -> list[dict[str, Any]]:
    return [e for e in read_events() if e.get("card") == card]


def snapshot(card: str, *, root: Path | None = None) -> Path:
    root = root or repo_root()
    events = events_for_card(card)
    blocks = [e for e in events if e.get("event") == "gateway_block"]
    rewards = [float(e.get("reward", 0)) for e in events if "reward" in e]
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0

    failures: list[dict[str, Any]] = []
    for e in blocks:
        blockers = e.get("blockers") or ["unknown"]
        failures.append(
            {
                "stage": e.get("stage", ""),
                "reason": blockers[0],
                "ts": e.get("ts", ""),
            }
        )

    procedures: list[str] = []
    for e in events:
        proc = (e.get("outcome") or {}).get("procedure")
        if proc and proc not in procedures:
            procedures.append(str(proc))

    human_notes = [str(e["human_note"]) for e in events if e.get("human_note")]

    payload: dict[str, Any] = {
        "card": card,
        "generated_at": _now_iso(),
        "run_summary": {
            "total_events": len(events),
            "gateway_blocks": len(blocks),
            "avg_reward": round(avg_reward, 3),
            "total_reward": round(sum(rewards), 3),
        },
        "stage_trace": [
            {
                "ts": e.get("ts"),
                "stage": e.get("stage"),
                "agent": e.get("agent"),
                "event": e.get("event"),
                "reward": e.get("reward"),
            }
            for e in events
        ],
        "failures": failures,
        "procedures_used": procedures,
        "context_for_future": human_notes[-5:],
    }

    out = root / ".sdlc" / "memory" / f"execution-{card}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def tail(n: int = 20) -> list[dict[str, Any]]:
    return read_events()[-n:]


def status_text() -> str:
    events = read_events()
    gate = load_session_gate()
    lines = [
        f"ledger: {LEDGER_PATH.relative_to(ROOT)}",
        f"events: {len(events)}",
        f"gate: {gate.get('gate_status', 'closed')}",
        f"card: {gate.get('card') or '(none)'}",
    ]
    if events:
        last = events[-1]
        lines.append(
            f"last: {last.get('event')} @ {last.get('ts')} reward={last.get('reward')}"
        )
    return "\n".join(lines)


def cmd_append(args: argparse.Namespace) -> int:
    if args.json:
        event = json.loads(args.json)
    else:
        event = build_gateway_event(
            event_type=args.event,
            reason=args.reason or "",
            evidence_verified=(
                None
                if args.evidence_verified == "unset"
                else args.evidence_verified == "true"
            ),
        )
    path = append_event(event)
    print(f"OK: appended → {path}")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    card = args.card or load_session_gate().get("card") or ""
    if not card:
        print("ERROR: --card required or open gate with card", file=sys.stderr)
        return 1
    out = snapshot(card)
    append_event(
        {
            "session_id": session_id(),
            "card": card,
            "branch": load_session_gate().get("branch", ""),
            "stage": load_session_gate().get("stage", ""),
            "agent": "workflow",
            "event": "workflow_finish",
            "outcome": {"handoff_complete": True},
            "reward": 1.0,
            "blockers": [],
            "human_note": f"Snapshot written to {out.name}",
        }
    )
    print(f"OK: snapshot → {out}")
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    for event in tail(args.n):
        print(json.dumps(event, ensure_ascii=False))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    print(status_text())
    return 0


def cmd_prune(args: argparse.Namespace) -> int:
    removed = prune_ledger(args.max)
    print(f"OK: pruned {removed} lines")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SDLC execution ledger (Harness v6)")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("append", help="Append one ledger event")
    a.add_argument("--event", default="stage_complete")
    a.add_argument("--reason", default="")
    a.add_argument(
        "--evidence-verified",
        choices=("true", "false", "unset"),
        default="unset",
    )
    a.add_argument("--json", help="Raw JSON event object")

    s = sub.add_parser("snapshot", help="Build execution-RPG-N.json from ledger")
    s.add_argument("--card", default="")

    t = sub.add_parser("tail", help="Print last N events")
    t.add_argument("-n", type=int, default=20)

    sub.add_parser("status", help="Ledger summary")

    p = sub.add_parser("prune", help="Trim ledger to max lines")
    p.add_argument("--max", type=int, default=MAX_LEDGER_LINES)

    args = parser.parse_args(argv)
    handlers = {
        "append": cmd_append,
        "snapshot": cmd_snapshot,
        "tail": cmd_tail,
        "status": cmd_status,
        "prune": cmd_prune,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
