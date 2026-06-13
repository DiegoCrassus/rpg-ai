"""Delegate to learning policy_optimizer (Harness v6)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
sys.path.insert(0, str(LEARNING))

from policy_optimizer import analyze  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SDLC optimization analyzer (legacy wrapper)")
    parser.add_argument("--last", type=int, default=100)
    parser.add_argument("--min-frequency", type=int, default=3)
    args = parser.parse_args(argv)
    report = analyze(args.last, min_frequency=args.min_frequency)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
