"""Lifecycle transition checks for workflow start."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _transition_edges(model: dict[str, Any]) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for tr in model.get("transitions") or []:
        f = tr.get("from_stage")
        t = tr.get("to_stage")
        if f and t:
            edges.add((str(f), str(t)))
    return edges


def gate_stage_to_lifecycle(gate_stage: str, aliases: dict[str, list[str]]) -> list[str]:
    if gate_stage in aliases:
        return list(aliases[gate_stage])
    return [gate_stage]


def transition_allowed(
    from_gate_stage: str,
    to_gate_stage: str,
    *,
    root: Path | None = None,
) -> tuple[bool, str]:
    """Return (allowed, message). Empty from_gate allows any to_gate (fresh start)."""
    if not to_gate_stage:
        return False, "target stage unset"
    if to_gate_stage == "sdlc_meta":
        return True, "sdlc_meta allows SDLC path edits"
    if not from_gate_stage or from_gate_stage == to_gate_stage:
        return True, "fresh start or same stage"

    try:
        from gate import repo_root  # noqa: PLC0415
        from lifecycle_model import gate_stage_aliases, load_model  # noqa: PLC0415
    except ImportError as exc:
        return True, f"skip transition check: {exc}"

    base = root or repo_root()
    model = load_model(base)
    if not model:
        return True, "no lifecycle model — skip"

    aliases = gate_stage_aliases(base)
    edges = _transition_edges(model)
    from_lifecycle = gate_stage_to_lifecycle(from_gate_stage, aliases)
    to_lifecycle = gate_stage_to_lifecycle(to_gate_stage, aliases)

    for f in from_lifecycle:
        for t in to_lifecycle:
            if (f, t) in edges:
                return True, f"transition {f} → {t}"
            if f == t:
                return True, f"same lifecycle stage {f}"

    return False, (
        f"illegal gate transition {from_gate_stage!r} → {to_gate_stage!r} "
        f"(lifecycle {from_lifecycle} → {to_lifecycle}); use SDLC_BREAK_GLASS or advance via pipeline"
    )
