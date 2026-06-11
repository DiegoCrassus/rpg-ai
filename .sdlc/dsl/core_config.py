"""Load vendor-neutral core section from .sdlc/sdlc.yaml."""

from __future__ import annotations

import re
from pathlib import Path
from re import Pattern
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _sdlc_path(root: Path) -> Path:
    return root / ".sdlc" / "sdlc.yaml"


def load_core(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    path = _sdlc_path(root)
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("core") or {}


def _vendors(root: str | Path) -> dict[str, Any]:
    return load_core(root).get("vendors") or {}


def board(root: str | Path) -> dict[str, Any]:
    """Workboard vendor config (logical role: board)."""
    vendors = _vendors(root)
    return vendors.get("board") or vendors.get("workboard") or {}


def workboard(root: str | Path) -> dict[str, Any]:
    """Deprecated alias for board()."""
    return board(root)


def repository(root: str | Path) -> dict[str, Any]:
    """Repository/VCS vendor config (logical role: repository)."""
    vendors = _vendors(root)
    return vendors.get("repository") or vendors.get("vcs") or {}


def vcs(root: str | Path) -> dict[str, Any]:
    """Deprecated alias for repository()."""
    return repository(root)


def env_map(root: str | Path) -> dict[str, str]:
    """Logical env name -> OS variable name."""
    return load_core(root).get("env") or {}


def card_prefix(root: str | Path) -> str:
    return str(board(root).get("card_prefix") or "RPG")


def card_id(sequence: int | str, root: str | Path | None = None) -> str:
    root = root or Path(__file__).resolve().parents[2]
    return f"{card_prefix(root)}-{int(sequence)}"


def card_pattern(root: str | Path) -> Pattern[str]:
    prefix = card_prefix(root)
    return re.compile(rf"^{re.escape(prefix)}-(\d+)$", re.IGNORECASE)


def card_reference_pattern(root: str | Path) -> Pattern[str]:
    prefix = card_prefix(root)
    return re.compile(rf"{re.escape(prefix)}-(\d+)", re.IGNORECASE)


def skill_path(root: str | Path, rel: str) -> Path:
    """Resolve skill path from catalog relative path."""
    root = Path(root)
    return root / rel


def gates(root: str | Path) -> dict[str, Any]:
    return load_core(root).get("gates") or {}


def gate_enforcement(root: str | Path) -> str:
    """Return gate enforcement mode: strict (default) or off."""
    raw = gates(root).get("enforcement", "strict")
    if raw is False:
        return "off"
    mode = str(raw).strip().lower().strip("'\"")
    if mode in ("off", "disabled", "false", "0", "no"):
        return "off"
    return "strict"


def set_gate_enforcement(root: str | Path, mode: str) -> Path:
    """Persist core.gates.enforcement in sdlc.yaml (strict | off)."""
    if mode not in ("strict", "off"):
        raise ValueError(f"Invalid gate enforcement mode: {mode!r} (expected strict|off)")
    root = Path(root)
    path = _sdlc_path(root)
    if yaml is None or not path.is_file():
        raise FileNotFoundError(f"Missing SDLC manifest: {path}")

    text = path.read_text(encoding="utf-8")
    yaml_value = "off" if mode == "off" else "strict"
    display = f"'{yaml_value}'" if mode == "off" else yaml_value
    pattern = re.compile(
        r"^(\s+enforcement:\s*)(?:'off'|\"off\"|off|strict|'strict'|\"strict\"|false|true)(\s*(?:#.*)?)$",
        re.M,
    )
    if pattern.search(text):
        updated = pattern.sub(rf"\g<1>{display}\g<2>", text, count=1)
    else:
        anchor = re.compile(r"^(\s+conventions:\s*$)", re.M)
        block = (
            "  gates:\n"
            "    # strict — protected paths require open gate + matching stage.\n"
            "    # off    — skip write-gate checks (structural / greenfield pivot).\n"
            f"    enforcement: {display}\n"
        )
        match = anchor.search(text)
        if not match:
            raise ValueError("Cannot locate core.conventions in sdlc.yaml to insert gates block")
        insert_at = match.start()
        updated = text[:insert_at] + block + text[insert_at:]

    path.write_text(updated, encoding="utf-8")
    return path
