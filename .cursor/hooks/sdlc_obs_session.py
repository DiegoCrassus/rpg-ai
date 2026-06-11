#!/usr/bin/env python3
"""
Cursor hook adapter for SDLC observability.

Usage (from hooks.json):
    sessionStart → python3 .cursor/hooks/sdlc_obs_session.py pre
    stop         → python3 .cursor/hooks/sdlc_obs_session.py post
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRE = REPO / "app/infra/sdlc_obs/hooks/pre_task.py"
POST = REPO / "app/infra/sdlc_obs/hooks/post_task.py"


def read_hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def extract_task(data: dict) -> str:
    if task := os.environ.get("SDLC_OBS_TASK"):
        return task

    for key in ("prompt", "user_message", "message", "text"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            line = val.strip().split("\n")[0][:120]
            return line if line.startswith("[AI]") else f"[AI][SESSION] {line}"

    return "[AI][SESSION] Cursor agent session"


def run_pre(data: dict) -> int:
    cmd = [
        sys.executable,
        str(PRE),
        "--task",
        extract_task(data),
        "--stage",
        os.environ.get("SDLC_OBS_STAGE", "implementation"),
        "--agent",
        os.environ.get("SDLC_OBS_AGENT", "implementer"),
        "--tags",
        "[AI]",
    ]
    return subprocess.run(cmd, cwd=REPO).returncode


def run_post() -> int:
    cmd = [
        sys.executable,
        str(POST),
        "--status",
        os.environ.get("SDLC_OBS_STATUS", "completed"),
    ]
    return subprocess.run(cmd, cwd=REPO).returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pre", "post"])
    args = parser.parse_args()

    data = read_hook_input() if args.mode == "pre" else {}

    if args.mode == "pre":
        run_pre(data)
    else:
        run_post()

    # Fail open — observability must not block the agent.
    sys.exit(0)


if __name__ == "__main__":
    main()
