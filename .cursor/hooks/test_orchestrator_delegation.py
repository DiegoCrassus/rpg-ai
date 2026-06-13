"""Tests for orchestrator delegation enforcement (gateway bypass prevention)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import sdlc_gateway_lib as gateway  # noqa: E402
import sdlc_gate_hook as gate_hook  # noqa: E402
import sdlc_pre_gateway as pre_gateway  # noqa: E402

POLICY = {
    "valid_agents": [
        "implementer",
        "qa",
        "reviewer",
        "devops",
        "none",
    ],
    "orchestrator_delegation": {
        "pipeline_agents": ["implementer", "qa", "reviewer", "devops"],
        "delegated_prefixes": [".sdlc/", ".cursor/", "app/"],
        "orchestrator_allowlist": [".sdlc/memory/operational-context.md"],
        "orchestrator_shell_allow_patterns": [r"^git\s+status\b"],
        "shell_agent_patterns": {
            "implementer": [r"\bgit\s+commit\b"],
            "devops": [r"\bgh\s+pr\s+create\b"],
            "qa": [r"\bpytest\b"],
        },
    },
    "handoff": {
        "required_sections": ["Routing", "Session", "Scope", "Blockers"],
        "required_fields": {
            "Routing": ["Next agent", "Stage complete", "Previous agent"],
            "Session": ["Card", "Branch", "Stage"],
        },
        "complete_values": ["yes", "no"],
        "empty_values": ["", "-", "none"],
    },
}


def _handoff(next_agent: str = "implementer") -> str:
    return f"""# Orchestrator Handoff (latest)

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | {next_agent} |
| **Stage complete** | no |
| **Previous agent** | orchestrator |

## Session

| Field | Value |
|-------|-------|
| **Card** | RPG-18 |
| **Branch** | feature/RPG-18-warm-learning-loop |
| **Stage** | sdlc_meta |

## Scope

Delegation test.

## Blockers

- none
"""


@pytest.fixture
def gateway_env(tmp_path, monkeypatch):
    handoff = tmp_path / "orchestrator-handoff.md"
    gate = tmp_path / "session-gate.json"
    handoff.write_text(_handoff("implementer"), encoding="utf-8")
    gate.write_text(
        json.dumps({"gate_status": "open", "stage": "sdlc_meta", "meta": {}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff)
    monkeypatch.setattr(gateway, "SESSION_GATE_PATH", gate)
    monkeypatch.setattr(gateway, "_gate_enforcement_off", lambda: False)
    return handoff, gate


def test_orchestrator_write_blocked_on_delegated_path(gateway_env, capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        gateway.enforce_orchestrator_delegation_write(
            ".sdlc/scripts/qa_evidence.py",
            POLICY,
        )
    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
    assert "Task(implementer)" in payload["agent_message"]


def test_active_subagent_may_write_delegated_path(gateway_env) -> None:
    _, gate_path = gateway_env
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["meta"] = {"active_subagent": "implementer"}
    gate_path.write_text(json.dumps(gate), encoding="utf-8")

    gateway.enforce_orchestrator_delegation_write(".sdlc/scripts/qa_evidence.py", POLICY)


def test_orchestrator_allowlist_path_passes(gateway_env) -> None:
    gateway.enforce_orchestrator_delegation_write(
        ".sdlc/memory/operational-context.md",
        POLICY,
    )


def test_orchestrator_shell_git_commit_blocked(gateway_env, capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        gateway.enforce_orchestrator_delegation_shell("git commit -m test", POLICY)
    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"


def test_active_devops_may_run_gh_pr_create(gateway_env) -> None:
    handoff_path, gate_path = gateway_env
    handoff_path.write_text(_handoff("devops"), encoding="utf-8")
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["meta"] = {"active_subagent": "devops"}
    gate_path.write_text(json.dumps(gate), encoding="utf-8")

    gateway.enforce_orchestrator_delegation_shell(
        "gh pr create --base develop",
        POLICY,
    )


def test_mark_subagent_start_sets_session_meta(gateway_env) -> None:
    _, gate_path = gateway_env
    pre_gateway.mark_subagent_start(
        {"tool_input": {"subagent_type": "implementer"}},
        POLICY,
    )
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    assert gate["meta"]["active_subagent"] == "implementer"


def test_gate_hook_applies_delegation_before_protected_check(
    gateway_env, monkeypatch, capsys
) -> None:
    handoff_path, gate_path = gateway_env
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff_path)
    monkeypatch.setattr(gateway, "SESSION_GATE_PATH", gate_path)
    monkeypatch.setattr(gate_hook._gate, "is_gate_enforcement_off", lambda root: False)
    monkeypatch.setattr(gate_hook, "require_policy", lambda: POLICY)

    payload = json.dumps({"tool_input": {"path": ".sdlc/scripts/foo.py"}})
    sys.stdin = io.StringIO(payload)
    with pytest.raises(SystemExit) as exc_info:
        gate_hook.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "deny"
