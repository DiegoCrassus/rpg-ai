"""Cross-check manifest catalog agents vs gateways policy.valid_agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def catalog_agent_ids(root: Path) -> tuple[set[str], set[str]]:
    catalog = _load_yaml(root / ".sdlc" / "manifest" / "catalog.yaml")
    pipeline = {str(a.get("id")) for a in (catalog.get("agents") or {}).get("pipeline") or [] if a.get("id")}
    support = {str(a.get("id")) for a in (catalog.get("agents") or {}).get("support") or [] if a.get("id")}
    return pipeline, support


def policy_valid_agents(root: Path) -> set[str]:
    policy = _load_yaml(root / ".sdlc" / "gateways" / "policy.yaml")
    return {str(a) for a in (policy.get("valid_agents") or []) if a}


def policy_pipeline_agents(root: Path) -> set[str]:
    policy = _load_yaml(root / ".sdlc" / "gateways" / "policy.yaml")
    delegation = policy.get("orchestrator_delegation") or {}
    return {str(a) for a in (delegation.get("pipeline_agents") or []) if a}


def check_roster_sync(root: Path) -> list[tuple[str, str]]:
    """Return list of (level, message) findings."""
    findings: list[tuple[str, str]] = []
    pipeline, support = catalog_agent_ids(root)
    valid = policy_valid_agents(root)

    if not pipeline:
        findings.append(("WARN", "catalog.yaml has no agents.pipeline entries"))
        return findings
    if not valid:
        findings.append(("WARN", "gateways/policy.yaml has no valid_agents"))
        return findings

    extras_in_policy = valid - pipeline - support - {"none", "explore", "generalpurpose", "general-purpose", "shell"}
    missing_in_policy = pipeline - valid

    for agent in sorted(missing_in_policy):
        findings.append(
            ("FAIL", f"catalog pipeline agent '{agent}' missing from policy.valid_agents"),
        )
    for agent in sorted(extras_in_policy):
        findings.append(
            ("WARN", f"policy.valid_agents '{agent}' not in catalog pipeline/support"),
        )

    pipeline_delegation = policy_pipeline_agents(root)
    overlap = support & pipeline_delegation
    for agent in sorted(overlap):
        findings.append(
            (
                "WARN",
                f"support agent '{agent}' must not be in orchestrator_delegation.pipeline_agents",
            ),
        )

    if not findings:
        findings.append(("PASS", "catalog pipeline agents synced with policy.valid_agents"))
    return findings
