#!/usr/bin/env python3
"""Post-subagent learning hook — record task event (fail-open)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / ".sdlc" / "scripts" / "learning_loop.py"


def main() -> None:
    try:
        read_payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        read_payload = {}
    _ = read_payload
    if not SCRIPT.is_file():
        print(json.dumps({}))
        return
    subprocess.run(
        [sys.executable, str(SCRIPT), "record-session"],
        cwd=REPO,
        capture_output=True,
    )
    print(json.dumps({}))


if __name__ == "__main__":
    main()
