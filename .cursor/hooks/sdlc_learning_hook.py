#!/usr/bin/env python3
"""Post-subagent learning hook — record task event (fail-open)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOKS = Path(__file__).resolve().parent
SCRIPT = REPO / ".sdlc" / "scripts" / "learning_loop.py"

if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

from sdlc_gateway_lib import extract_subagent, read_payload  # noqa: E402


def _stage_complete_no() -> bool:
    handoff = REPO / ".sdlc" / "memory" / "orchestrator-handoff.md"
    if not handoff.is_file():
        return False
    text = handoff.read_text(encoding="utf-8").lower()
    return "**stage complete** | `no`" in text or "**stage complete** | no" in text


def main() -> None:
    payload = read_payload()
    agent = extract_subagent(payload) or ""

    if not SCRIPT.is_file():
        print(json.dumps({}))
        return

    cmd = [sys.executable, str(SCRIPT), "record-session"]
    if agent:
        cmd.extend(["--agent", agent])
    if _stage_complete_no():
        cmd.append("--gateway-block")

    subprocess.run(cmd, cwd=REPO, capture_output=True)
    print(json.dumps({}))


if __name__ == "__main__":
    main()
