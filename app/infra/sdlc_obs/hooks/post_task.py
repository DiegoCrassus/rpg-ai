#!/usr/bin/env python3
"""Post-task hook — close SDLC observability run."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.infra.sdlc_obs.collector import Collector  # noqa: E402
from app.infra.sdlc_obs.store import EventStore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="completed")
    parser.add_argument("--cost", type=float, default=0.0)
    parser.add_argument("--tokens-in", type=int, default=0)
    parser.add_argument("--tokens-out", type=int, default=0)
    parser.add_argument("--tools-total", type=int, default=0)
    parser.add_argument("--tools-ok", type=int, default=0)
    parser.add_argument("--tests-pass", type=int, default=0)
    parser.add_argument("--tests-fail", type=int, default=0)
    parser.add_argument("--doctor", type=int, default=None)
    args = parser.parse_args()

    state_path = ROOT / ".sdlc_obs_state.json"
    run_id = ""
    started_at = None
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            run_id = str(state.get("run_id") or "")
            started_at = state.get("started_at")
        except (OSError, json.JSONDecodeError):
            pass

    duration_ms = 0
    if started_at:
        duration_ms = int((time.time() - float(started_at)) * 1000)

    hallucination = (
        args.tests_fail > 0
        or (args.doctor is not None and args.doctor != 0)
    ) and args.status == "completed"

    collector = Collector()
    if run_id:
        collector.end(
            run_id,
            completion_status=args.status,
            duration_ms=duration_ms,
            tokens_input=args.tokens_in,
            tokens_output=args.tokens_out,
            cost_usd=args.cost,
            tool_calls_total=args.tools_total,
            tool_calls_success=args.tools_ok,
            tool_calls_failed=max(0, args.tools_total - args.tools_ok),
            tests_passed=args.tests_pass,
            tests_failed=args.tests_fail,
            doctor_exit_code=args.doctor,
            hallucination_flag=hallucination,
        )
        store = EventStore()
        store.append_event(
            event_type="obs.run_ended",
            source="sdlc_obs",
            category="obs",
            correlation={"run_id": run_id},
            payload={
                "completion_status": args.status,
                "duration_ms": duration_ms,
                "doctor_exit_code": args.doctor,
                "tests_passed": args.tests_pass,
                "tests_failed": args.tests_fail,
                "hallucination_flag": hallucination,
            },
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
