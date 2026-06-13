"""Tests for orchestrator handoff shell bypass denial (policy + gateway)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / ".cursor" / "hooks"
POLICY_PATH = REPO_ROOT / ".sdlc" / "gateways" / "policy.yaml"

if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import sdlc_gateway_lib as gateway  # noqa: E402


def _load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}


def test_policy_has_orchestrator_handoff_shell_deny_patterns() -> None:
    policy = _load_policy()
    patterns = (policy.get("orchestrator_delegation") or {}).get(
        "orchestrator_shell_deny_patterns"
    ) or []
    assert patterns, "orchestrator_shell_deny_patterns must be configured"
    joined = " ".join(str(p) for p in patterns)
    assert "orchestrator-handoff" in joined


@pytest.fixture
def gateway_env(tmp_path, monkeypatch):
    handoff = tmp_path / "orchestrator-handoff.md"
    gate = tmp_path / "session-gate.json"
    handoff.write_text(
        "# Orchestrator Handoff\n\n## Routing\n\n| **Next agent** | implementer |\n",
        encoding="utf-8",
    )
    gate.write_text(
        json.dumps({"gate_status": "open", "stage": "sdlc_meta", "meta": {}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff)
    monkeypatch.setattr(gateway, "SESSION_GATE_PATH", gate)
    monkeypatch.setattr(gateway, "_gate_enforcement_off", lambda: False)
    return handoff, gate


def test_orchestrator_python_handoff_write_blocked(gateway_env, capsys) -> None:
    policy = _load_policy()
    cmd = (
        'python -c "open(\'.sdlc/memory/orchestrator-handoff.md\',\'w\').write(\'# x\')"'
    )
    with pytest.raises(SystemExit) as exc_info:
        gateway.enforce_orchestrator_delegation_shell(cmd, policy)
    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
    assert "handoff" in payload["agent_message"].lower()


def test_orchestrator_shell_redirect_handoff_blocked(gateway_env, capsys) -> None:
    policy = _load_policy()
    cmd = "echo bypass > .sdlc/memory/orchestrator-handoff.md"
    with pytest.raises(SystemExit) as exc_info:
        gateway.enforce_orchestrator_delegation_shell(cmd, policy)
    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
