#!/usr/bin/env python3
"""CLI — token budget status / reset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))

from token_budget import reset_session, status_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SDLC token budget")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Print ledger")
    sub.add_parser("reset", help="Reset session counters")
    args = parser.parse_args()

    if args.cmd == "status":
        print(status_text(ROOT))
        return 0
    reset_session(ROOT)
    print("OK: token budget session reset")
    print(status_text(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
