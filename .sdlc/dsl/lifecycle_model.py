"""Load canonical lifecycle model from `.sdlc/process/lifecycle-model.yaml`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def model_path(root: Path) -> Path:
    return root / ".sdlc" / "process" / "lifecycle-model.yaml"


def load_model(root: Path | None = None) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required for lifecycle model")
    from gate import repo_root  # noqa: PLC0415

    base = root or repo_root()
    path = model_path(base)
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def load_write_policy(root: Path | None = None) -> dict[str, Any]:
    """Return gate_paths-shaped dict (protected_prefixes + stages)."""
    model = load_model(root)
    policy = model.get("write_policy") or {}
    if policy:
        return policy
    from gate import gate_config_path, repo_root  # noqa: PLC0415

    base = root or repo_root()
    legacy = gate_config_path(base)
    if yaml and legacy.is_file():
        with legacy.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("gate_paths") or {}
    return {}


def lifecycle_stage_ids(root: Path | None = None) -> set[str]:
    model = load_model(root)
    return {str(s.get("id")) for s in (model.get("stages") or []) if s.get("id")}


def gate_stage_aliases(root: Path | None = None) -> dict[str, list[str]]:
    model = load_model(root)
    raw = model.get("gate_stage_aliases") or {}
    return {str(k): list(v) for k, v in raw.items() if isinstance(v, list)}


def transition_overlay(root: Path | None = None) -> dict[str, dict[str, Any]]:
    """Legacy workflows/transitions.yaml metadata keyed by transition id (graph from model)."""
    if yaml is None:
        return {}
    from gate import repo_root  # noqa: PLC0415

    base = root or repo_root()
    path = base / ".sdlc" / "workflows" / "transitions.yaml"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    workflows = data.get("workflows") if isinstance(data, dict) else []
    return {str(w["id"]): w for w in workflows or [] if w.get("id")}
