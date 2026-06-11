#!/usr/bin/env python3
"""Verify lifecycle-model write_policy matches gates/paths.yaml shim (warn on drift)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))
    import yaml  # noqa: E402
    from lifecycle_model import load_write_policy, model_path  # noqa: E402

    model_policy = load_write_policy(ROOT)
    legacy_path = ROOT / ".sdlc" / "gates" / "paths.yaml"
    legacy_policy = {}
    if legacy_path.is_file():
        data = yaml.safe_load(legacy_path.read_text(encoding="utf-8")) or {}
        legacy_policy = data.get("gate_paths") or {}

    if not model_policy:
        print("FAIL: lifecycle-model write_policy empty", file=sys.stderr)
        return 1

    if model_policy == legacy_policy:
        print("OK: lifecycle-model write_policy matches paths.yaml shim")
        return 0

    print("WARN: lifecycle-model and paths.yaml differ (shim drift)", file=sys.stderr)
    print(f"  model: {model_path(ROOT)}", file=sys.stderr)
    print(f"  legacy: {legacy_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
