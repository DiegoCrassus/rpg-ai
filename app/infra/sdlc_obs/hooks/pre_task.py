#!/usr/bin/env python3
"""Pre-task hook — start SDLC observability run."""

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


def _gate_context() -> tuple[str, str]:
    gate_path = ROOT / ".sdlc" / "memory" / "session-gate.json"
    if not gate_path.is_file():
        return "", ""
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        return str(gate.get("card") or ""), str(gate.get("branch") or "")
    except (OSError, json.JSONDecodeError):
        return "", ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--stage", default="implementation")
    parser.add_argument("--agent", default="implementer")
    parser.add_argument("--tags", default="[AI]")
    args = parser.parse_args()

    card, branch = _gate_context()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    collector = Collector()
    run_id = collector.start(
        task_name=args.task,
        stage=args.stage,
        agent=args.agent,
        task_tags=tags or ["[AI]"],
        card=card,
        branch=branch,
    )
    state_path = ROOT / ".sdlc_obs_state.json"
    state_path.write_text(
        json.dumps({"run_id": run_id, "started_at": time.time()}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
