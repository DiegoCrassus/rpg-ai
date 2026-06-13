"""Tests for support agents skill-only invocation model."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DSL = REPO_ROOT / ".sdlc" / "dsl"
HOOKS = REPO_ROOT / ".cursor" / "hooks"

if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import sdlc_pre_gateway as pre_gateway  # noqa: E402
from roster_sync import catalog_agent_ids, check_roster_sync  # noqa: E402

CATALOG_PATH = REPO_ROOT / ".sdlc" / "manifest" / "catalog.yaml"
POLICY_PATH = REPO_ROOT / ".sdlc" / "gateways" / "policy.yaml"

EXPECTED_SUPPORT = {
    "doctor",
    "observer",
    "issue-analyst",
    "sdlc-auditor",
    "security-scanner",
    "migration-runner",
    "contract-validator",
    "rollback-agent",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_catalog_support_has_skill_only_invocation() -> None:
    catalog = _load_yaml(CATALOG_PATH)
    support = (catalog.get("agents") or {}).get("support") or []
    assert support, "catalog agents.support must not be empty"

    ids = {entry["id"] for entry in support}
    assert ids == EXPECTED_SUPPORT

    for entry in support:
        assert entry.get("invocation") == "skill-only", (
            f"support agent {entry.get('id')} missing invocation: skill-only"
        )


def test_doctor_maps_structural_validation_skill() -> None:
    catalog = _load_yaml(CATALOG_PATH)
    support = (catalog.get("agents") or {}).get("support") or []
    doctor = next(item for item in support if item.get("id") == "doctor")

    assert doctor.get("skill_id") == "structural-validation"
    assert doctor.get("command_id") == "sdlc-doctor"


def test_policy_lists_support_agents() -> None:
    policy = _load_yaml(POLICY_PATH)
    listed = set(policy.get("support_agents") or [])
    assert listed == EXPECTED_SUPPORT

    spawn = policy.get("support_spawn") or {}
    assert spawn.get("bypass_handoff_route") is True
    assert spawn.get("description")


def test_support_agents_not_in_pipeline_delegation() -> None:
    policy = _load_yaml(POLICY_PATH)
    pipeline = set(
        (policy.get("orchestrator_delegation") or {}).get("pipeline_agents") or []
    )
    overlap = EXPECTED_SUPPORT & pipeline
    assert not overlap, f"support agents must not be pipeline_agents: {sorted(overlap)}"


def test_roster_sync_warns_on_support_pipeline_overlap(tmp_path: Path) -> None:
    catalog_src = CATALOG_PATH.read_text(encoding="utf-8")
    policy_src = POLICY_PATH.read_text(encoding="utf-8")

    (tmp_path / ".sdlc" / "manifest").mkdir(parents=True)
    (tmp_path / ".sdlc" / "gateways").mkdir(parents=True)
    (tmp_path / ".sdlc" / "manifest" / "catalog.yaml").write_text(catalog_src, encoding="utf-8")

    policy = _load_yaml(POLICY_PATH)
    delegation = policy.setdefault("orchestrator_delegation", {})
    pipeline = list(delegation.get("pipeline_agents") or [])
    if "doctor" not in pipeline:
        pipeline.append("doctor")
    delegation["pipeline_agents"] = pipeline
    (tmp_path / ".sdlc" / "gateways" / "policy.yaml").write_text(
        yaml.safe_dump(policy, sort_keys=False),
        encoding="utf-8",
    )

    findings = check_roster_sync(tmp_path)
    messages = [msg for _level, msg in findings]
    assert any("support agent 'doctor'" in msg for msg in messages)


def test_pre_gateway_allows_doctor_without_matching_handoff(monkeypatch) -> None:
    policy = _load_yaml(POLICY_PATH)
    monkeypatch.setattr(
        pre_gateway,
        "routing",
        lambda _policy: {"next_agent": "qa"},
    )

    pre_gateway.enforce_next_subagent({"subagent_type": "doctor"}, policy)


def test_pre_gateway_still_blocks_pipeline_mismatch(capsys, monkeypatch) -> None:
    policy = _load_yaml(POLICY_PATH)
    monkeypatch.setattr(
        pre_gateway,
        "routing",
        lambda _policy: {"next_agent": "implementer"},
    )

    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.enforce_next_subagent({"subagent_type": "qa"}, policy)

    assert exc_info.value.code == 0
    import json

    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
    assert "expects 'implementer'" in payload["agent_message"]


def test_catalog_and_policy_support_ids_aligned() -> None:
    _pipeline, support = catalog_agent_ids(REPO_ROOT)
    policy = _load_yaml(POLICY_PATH)
    listed = set(policy.get("support_agents") or [])
    assert support == listed
