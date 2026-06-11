#!/usr/bin/env python3
"""Read-only discovery hook — legacy docs and repo state for Planner/Orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LEGACY_GLOBS = [
    "docs/product/*",
    "docs/architecture/*-api.md",
    "docs/product/**/*.md",
]

APP_PLACEHOLDER_MARKERS = ("not yet implemented", "placeholder", "tbd")


def app_is_placeholder() -> bool:
    for sub in ("backend", "frontend"):
        readme = ROOT / "app" / sub / "README.md"
        if not readme.is_file():
            return False
        text = readme.read_text(encoding="utf-8").lower()
        if not any(m in text for m in APP_PLACEHOLDER_MARKERS):
            files = [p for p in (ROOT / "app" / sub).rglob("*") if p.is_file() and p.name != "README.md"]
            if files:
                return False
    return True


def find_legacy_docs() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for pattern in LEGACY_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file():
                rel = path.relative_to(ROOT).as_posix()
                found.append({"path": rel, "reason": "legacy product/architecture doc"})
    return sorted(found, key=lambda x: x["path"])


def run_discovery() -> dict:
    return {
        "app_placeholder": app_is_placeholder(),
        "legacy_docs": find_legacy_docs(),
        "greenfield_hint": app_is_placeholder(),
        "recommendation": (
            "ignore legacy_docs for GREENFIELD" if app_is_placeholder() else "review legacy_docs before plan"
        ),
    }


def main() -> None:
    data = run_discovery()
    out_path = ROOT / ".sdlc" / "memory" / "discovery-context.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
