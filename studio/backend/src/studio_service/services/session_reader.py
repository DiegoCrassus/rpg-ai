"""Read session gate and orchestrator handoff from ``.sdlc/memory/``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_session_gate(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".sdlc/memory/session-gate.json"
    if not path.is_file():
        return {"present": False, "path": str(path.relative_to(repo_root)), "gate": None}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"present": True, "path": str(path.relative_to(repo_root)), "gate": data}


def read_handoff(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".sdlc/memory/orchestrator-handoff.md"
    if not path.is_file():
        return {
            "present": False,
            "path": str(path.relative_to(repo_root)),
            "raw": None,
            "sections": {},
        }
    raw = path.read_text(encoding="utf-8")
    return {
        "present": True,
        "path": str(path.relative_to(repo_root)),
        "raw": raw,
        "sections": _parse_handoff_tables(raw),
    }


def _parse_handoff_tables(text: str) -> dict[str, dict[str, str]]:
    """Extract markdown table rows as section -> field -> value."""

    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, {})
            continue
        if not line.startswith("|") or current is None:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("Field", "-------", "---"):
            continue
        key = cells[0].strip("* ")
        value = cells[1].strip()
        if key and value:
            sections[current][key] = value
    return sections
