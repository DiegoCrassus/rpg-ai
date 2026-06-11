#!/usr/bin/env python3
"""CLI for SDLC session gate — open, close, status, check, enforcement."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))

import gate as _gate  # noqa: E402

try:
    import core_config as _core  # noqa: E402
except ImportError:
    _core = None  # type: ignore[assignment]


def _cmd_enforcement(args: argparse.Namespace) -> None:
    if _core is None:
        print("ERROR: core_config unavailable", file=sys.stderr)
        sys.exit(1)

    if args.enforcement_command == "status":
        mode = _gate.gate_enforcement_mode(ROOT)
        source = "SDLC_GATES env" if mode == "off" and __import__("os").environ.get("SDLC_GATES") else "sdlc.yaml"
        print(f"gate_enforcement: {mode} ({source})")
        if mode == "off":
            print("WARN: write-gate checks are disabled — re-enable with: enforcement strict", file=sys.stderr)
        return

    mode = "off" if args.enforcement_command == "off" else "strict"
    path = _core.set_gate_enforcement(ROOT, mode)
    print(f"OK: gate enforcement set to {mode} in {path.relative_to(ROOT).as_posix()}")
    if mode == "off":
        print(
            "WARN: protected paths (app/, pyproject.toml) are writable without gate — "
            "document on Plane SDLC_META card and run `enforcement strict` when done.",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="SDLC session gate")
    sub = parser.add_subparsers(dest="command", required=True)

    o = sub.add_parser("open", help="Open gate for a card/stage")
    o.add_argument("--card", required=True)
    o.add_argument("--branch", default="")
    o.add_argument("--stage", required=True)
    o.add_argument("--intent", default="")

    sub.add_parser("close", help="Close gate")
    sub.add_parser("status", help="Print gate status")

    c = sub.add_parser("check", help="Check if path is writable")
    c.add_argument("--path", required=True)

    enf = sub.add_parser("enforcement", help="Show or change gate enforcement (sdlc.yaml)")
    enf_sub = enf.add_subparsers(dest="enforcement_command", required=True)
    enf_sub.add_parser("status", help="Show enforcement mode")
    enf_sub.add_parser("off", help="Disable write-gate checks (structural / pivot work)")
    enf_sub.add_parser("strict", help="Re-enable write-gate checks (default)")

    args = parser.parse_args()

    if args.command == "open":
        state = _gate.open_gate(
            card=args.card,
            branch=args.branch,
            stage=args.stage,
            intent=args.intent,
        )
        print(f"OK: gate open — {state.card} stage={state.stage}")
    elif args.command == "close":
        _gate.close_gate()
        print("OK: gate closed")
    elif args.command == "status":
        print(_gate.gate_status_text())
    elif args.command == "check":
        ok, msg = _gate.check_write(args.path)
        if ok:
            print(f"OK: {msg}")
        else:
            print(f"DENY: {msg}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "enforcement":
        _cmd_enforcement(args)


if __name__ == "__main__":
    main()
