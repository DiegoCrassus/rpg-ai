#!/usr/bin/env python3
"""Structural audit helper for SDLC observability paths."""

from __future__ import annotations

import sys
from pathlib import Path


def _repo_root() -> Path:
    cur = Path(__file__).resolve()
    for _ in range(8):
        if (cur / ".sdlc").is_dir() and (cur / "Makefile").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path(__file__).resolve().parents[3]


def main() -> int:
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from app.infra.sdlc_obs.collector import Collector
    from app.infra.sdlc_obs.store import EventStore

    manifest = root / ".sdlc" / "runtime" / "manifest.yaml"
    errors: list[str] = []
    if not manifest.is_file():
        errors.append(f"missing runtime manifest: {manifest}")

    try:
        collector = Collector()
        store = EventStore(collector.db_path)
        _ = store.build_timeline(limit=1)
        _ = collector.get_kpis()
    except Exception as exc:
        errors.append(f"obs store init failed: {exc}")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("PASS: sdlc_obs auditor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
