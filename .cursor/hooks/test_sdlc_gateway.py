"""Tests for deterministic SDLC gateway routing and handoff behavior."""

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
import sdlc_post_gateway as post_gateway  # noqa: E402
import sdlc_pre_gateway as pre_gateway  # noqa: E402

POLICY = {
    "valid_agents": [
        "intent-analyst",
        "planner",
        "architect",
        "implementer",
        "qa",
        "reviewer",
        "devops",
        "none",
    ],
    "agent_order": {
        "implementer": {"fallback": "architect"},
        "qa": {"fallback": "implementer"},
        "reviewer": {"fallback": "implementer"},
    },
    "handoff": {
        "required_sections": ["Routing", "Session", "Scope", "Blockers"],
        "required_fields": {
            "Routing": ["Next agent", "Stage complete", "Previous agent"],
            "Session": ["Card", "Branch", "Stage"],
        },
        "complete_values": ["yes", "no"],
        "empty_values": ["", "-", "—", "(none)"],
    },
    "post_gateway": {
        "reroute_on_incomplete_stage": True,
        "reroute_on_blockers": True,
    },
}


def handoff_markdown(
    *,
    next_agent: str = "qa",
    stage_complete: str = "yes",
    previous_agent: str = "implementer",
    blockers: str = "- none",
) -> str:
    return f"""# Orchestrator Handoff (latest)

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | {next_agent} |
| **Stage complete** | {stage_complete} |
| **Previous agent** | {previous_agent} |

## Session

| Field | Value |
|-------|-------|
| **Card** | RPG-40 |
| **Branch** | feature/RPG-40-sdlc-v5-restore |
| **Stage** | sdlc_meta |

## Scope

Gateway test coverage.

## Blockers

{blockers}
"""


def test_parse_handoff_extracts_markdown_tables() -> None:
    parsed = gateway.parse_handoff(handoff_markdown(next_agent="QA", stage_complete="No"))

    assert "Routing" in parsed["sections"]
    assert gateway.handoff_value(parsed, "Routing", "Next agent") == "QA"
    assert gateway.handoff_value(parsed, "Routing", "stage COMPLETE") == "No"
    assert gateway.normalize_agent("Intent Analyst.md") == "intent-analyst"


def test_validate_handoff_accepts_complete_markdown(tmp_path, monkeypatch) -> None:
    handoff_path = tmp_path / "orchestrator-handoff.md"
    handoff_path.write_text(handoff_markdown(), encoding="utf-8")
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff_path)

    assert gateway.validate_handoff(POLICY) == []


def test_validate_handoff_reports_contract_problems(tmp_path, monkeypatch) -> None:
    handoff_path = tmp_path / "orchestrator-handoff.md"
    handoff_path.write_text(
        handoff_markdown(next_agent="unknown-agent", stage_complete="maybe").replace(
            "## Blockers", "## Missing Blockers"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff_path)

    problems = gateway.validate_handoff(POLICY)

    assert "missing section: Blockers" in problems
    assert "Routing.Stage complete must be yes or no" in problems
    assert "Routing.Next agent is unknown: unknown-agent" in problems


def test_validate_handoff_rejects_yaml_fence(tmp_path, monkeypatch) -> None:
    handoff_path = tmp_path / "orchestrator-handoff.md"
    handoff_path.write_text("```yaml\nnext_agent: qa\n```\n", encoding="utf-8")
    monkeypatch.setattr(gateway, "HANDOFF_PATH", handoff_path)

    assert gateway.validate_handoff(POLICY) == [
        "handoff must be Markdown, not a YAML code fence"
    ]


def test_pre_gateway_enforces_current_subagent_route(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        pre_gateway,
        "routing",
        lambda policy: {"next_agent": "implementer"},
    )

    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.enforce_next_subagent(
            {"tool_input": {"subagent_type": "qa"}},
            POLICY,
        )

    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
    assert "expects 'implementer'" in payload["agent_message"]


def test_pre_gateway_allows_expected_and_generic_agents(monkeypatch) -> None:
    monkeypatch.setattr(
        pre_gateway,
        "routing",
        lambda policy: {"next_agent": "implementer"},
    )

    pre_gateway.enforce_next_subagent({"subagent_type": "implementer"}, POLICY)
    pre_gateway.enforce_next_subagent({"subagent_type": "explore"}, POLICY)


def test_pre_gateway_blocks_unsafe_shell_command(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.deny_unsafe_shell(
            "git reset --hard HEAD",
            {
                "pre_gateway": {
                    "deny_shell_patterns": [r"git\s+reset\s+--hard"],
                    "deny_message": "blocked",
                }
            },
        )

    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["permission"] == "deny"
    assert "deterministic deny pattern" in payload["agent_message"]


def test_post_gateway_blocks_incomplete_stage(capsys, monkeypatch) -> None:
    handoff = handoff_markdown(stage_complete="no")
    monkeypatch.setattr(post_gateway, "require_policy", lambda: POLICY)
    monkeypatch.setattr(post_gateway, "validate_handoff", lambda policy: [])
    monkeypatch.setattr(
        post_gateway,
        "routing",
        lambda policy: {
            "previous_agent": "implementer",
            "next_agent": "qa",
            "stage_complete": "no",
            "blockers": "- none",
        },
    )
    monkeypatch.setattr(post_gateway, "read_handoff", lambda: handoff)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))

    with pytest.raises(SystemExit) as exc_info:
        post_gateway.main()

    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "Return to `qa`" in payload["followup_message"]
    assert "stage is explicitly incomplete" in payload["followup_message"]


def test_post_gateway_blocks_unresolved_blockers(capsys, monkeypatch) -> None:
    handoff = handoff_markdown(blockers="- Reviewer requested more tests")
    monkeypatch.setattr(post_gateway, "require_policy", lambda: POLICY)
    monkeypatch.setattr(post_gateway, "validate_handoff", lambda policy: [])
    monkeypatch.setattr(
        post_gateway,
        "routing",
        lambda policy: {
            "previous_agent": "reviewer",
            "next_agent": "implementer",
            "stage_complete": "yes",
            "blockers": "- Reviewer requested more tests",
        },
    )
    monkeypatch.setattr(post_gateway, "read_handoff", lambda: handoff)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))

    with pytest.raises(SystemExit) as exc_info:
        post_gateway.main()

    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "Return to `implementer`" in payload["followup_message"]
    assert "unresolved blockers" in payload["followup_message"]


def test_post_gateway_treats_active_qa_none_wording_as_clear() -> None:
    assert post_gateway.blockers_are_clear("- None for QA; implementation is ready")
