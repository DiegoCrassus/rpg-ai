#!/usr/bin/env python3
"""Shared helpers for deterministic SDLC Cursor gateways."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / ".sdlc" / "gateways" / "policy.yaml"
POLICY_LOAD_DENY_USER = (
    "SDLC gateway could not load policy — interaction blocked (fail-closed)."
)
POLICY_LOAD_DENY_AGENT = (
    "Install PyYAML (`pip install pyyaml`) and ensure "
    f"{POLICY_PATH.relative_to(REPO)} exists, then retry."
)
HANDOFF_PATH = REPO / ".sdlc" / "memory" / "orchestrator-handoff.md"
OBS_STATE_PATH = REPO / ".sdlc_obs_state.json"
SESSION_GATE_PATH = REPO / ".sdlc" / "memory" / "session-gate.json"


def read_session_correlation() -> dict[str, Any]:
    correlation: dict[str, Any] = {}
    if SESSION_GATE_PATH.is_file():
        try:
            gate = json.loads(SESSION_GATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            gate = {}
        if isinstance(gate, dict):
            if card := gate.get("card"):
                correlation["card"] = str(card)
            if branch := gate.get("branch"):
                correlation["branch"] = str(branch)
    if OBS_STATE_PATH.is_file():
        try:
            state = json.loads(OBS_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}
        if isinstance(state, dict) and state.get("run_id"):
            correlation["run_id"] = str(state["run_id"])
    return correlation


def emit_studio_event(
    event_type: str,
    source: str,
    payload: dict[str, Any],
    *,
    category: str = "gateway",
) -> None:
    """Best-effort append to unified obs store; hooks must never fail on ingest errors."""

    try:
        import sys

        root = str(REPO)
        if root not in sys.path:
            sys.path.insert(0, root)
        from app.infra.sdlc_obs.store import EventStore  # type: ignore

        store = EventStore()
        store.append_event(
            event_type=event_type,
            source=source,
            payload=payload,
            correlation=read_session_correlation(),
            category=category,
        )
    except Exception:
        return


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return data if isinstance(data, dict) else {"payload": data}


def load_policy() -> dict[str, Any]:
    if yaml is None or not POLICY_PATH.is_file():
        return {}
    with POLICY_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def require_policy() -> dict[str, Any]:
    """Load gateway policy or deny the interaction (fail-closed)."""
    policy = load_policy()
    if policy:
        return policy
    if yaml is None:
        deny(POLICY_LOAD_DENY_USER, "PyYAML is not installed in the hook Python environment.")
    deny(POLICY_LOAD_DENY_USER, POLICY_LOAD_DENY_AGENT)
    return {}


def allow(extra: dict[str, Any] | None = None) -> None:
    result = {"permission": "allow"}
    if extra:
        result.update(extra)
    print(json.dumps(result))
    sys.exit(0)


def deny(
    user_message: str,
    agent_message: str,
    *,
    event_type: str | None = None,
    event_payload: dict[str, Any] | None = None,
) -> None:
    if event_type:
        payload = dict(event_payload or {})
        payload.setdefault("reason", agent_message)
        emit_studio_event(event_type, "sdlc_pre_gateway", payload, category="gateway")
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": user_message,
                "agent_message": agent_message,
            }
        )
    )
    sys.exit(0)


def first_string(data: Any, keys: tuple[str, ...]) -> str:
    if not isinstance(data, dict):
        return ""
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def nested_payload(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("tool_input", "input", "arguments", "params"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return payload


def extract_write_path(payload: dict[str, Any]) -> str:
    """Resolve target path from Cursor preToolUse Write payloads."""
    data = nested_payload(payload)
    return first_string(data, ("path", "file_path", "target_file"))


def extract_command(payload: dict[str, Any]) -> str:
    data = nested_payload(payload)
    return first_string(data, ("command", "cmd", "shell_command"))


def extract_subagent(payload: dict[str, Any]) -> str:
    data = nested_payload(payload)
    raw = first_string(
        data,
        (
            "subagent_type",
            "subagent",
            "agent",
            "agent_id",
            "description",
            "name",
        ),
    )
    return normalize_agent(raw)


def normalize_agent(value: str) -> str:
    v = (value or "").strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "intent": "intent-analyst",
        "intent-analyst.md": "intent-analyst",
        "auto-fixer.md": "auto-fixer",
        "autofixer": "auto-fixer",
        "implementer.md": "implementer",
        "planner.md": "planner",
        "architect.md": "architect",
        "qa.md": "qa",
        "reviewer.md": "reviewer",
        "devops.md": "devops",
        "doctor.md": "doctor",
    }
    return aliases.get(v, v)


def read_handoff() -> str:
    if not HANDOFF_PATH.is_file():
        return ""
    return HANDOFF_PATH.read_text(encoding="utf-8")


def parse_handoff(markdown: str) -> dict[str, Any]:
    sections: dict[str, str] = {}
    current = ""
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        sections[current] = "\n".join(lines).strip()

    fields: dict[str, dict[str, str]] = {}
    row_re = re.compile(r"^\|\s*(?:\*\*)?([^|*]+?)(?:\*\*)?\s*\|\s*([^|]+?)\s*\|$")
    for section, body in sections.items():
        section_fields: dict[str, str] = {}
        for line in body.splitlines():
            if set(line.strip()) <= {"|", "-", " "}:
                continue
            match = row_re.match(line.strip())
            if not match:
                continue
            key = match.group(1).strip().strip("*")
            value = match.group(2).strip().strip("*")
            if key.lower() != "field":
                section_fields[key] = value
        if section_fields:
            fields[section] = section_fields

    return {"sections": sections, "fields": fields}


def handoff_value(parsed: dict[str, Any], section: str, field: str) -> str:
    fields = parsed.get("fields") or {}
    section_fields = fields.get(section) or {}
    for key, value in section_fields.items():
        if key.lower() == field.lower():
            return str(value).strip()
    return ""


def is_empty_value(value: str, policy: dict[str, Any]) -> bool:
    empty_values = {
        str(v).lower()
        for v in ((policy.get("handoff") or {}).get("empty_values") or [])
    }
    return value.strip().lower() in empty_values


def validate_handoff(policy: dict[str, Any]) -> list[str]:
    markdown = read_handoff()
    if not markdown.strip():
        return ["handoff file is missing or empty"]
    if "```yaml" in markdown:
        return ["handoff must be Markdown, not a YAML code fence"]

    parsed = parse_handoff(markdown)
    handoff_policy = policy.get("handoff") or {}
    problems: list[str] = []

    sections = parsed.get("sections") or {}
    for section in handoff_policy.get("required_sections") or []:
        if section not in sections:
            problems.append(f"missing section: {section}")

    for section, fields in (handoff_policy.get("required_fields") or {}).items():
        for field in fields or []:
            value = handoff_value(parsed, section, field)
            if not value or is_empty_value(value, policy):
                problems.append(f"missing field: {section}.{field}")

    stage_complete = handoff_value(parsed, "Routing", "Stage complete").lower()
    complete_values = {
        str(v).lower() for v in handoff_policy.get("complete_values", [])
    }
    if stage_complete and complete_values and stage_complete not in complete_values:
        problems.append("Routing.Stage complete must be yes or no")

    next_agent = normalize_agent(handoff_value(parsed, "Routing", "Next agent"))
    valid_agents = set(policy.get("valid_agents") or [])
    if next_agent and valid_agents and next_agent not in valid_agents:
        problems.append(f"Routing.Next agent is unknown: {next_agent}")

    return problems


def routing(policy: dict[str, Any]) -> dict[str, str]:
    parsed = parse_handoff(read_handoff())
    previous = normalize_agent(handoff_value(parsed, "Routing", "Previous agent"))
    next_agent = normalize_agent(handoff_value(parsed, "Routing", "Next agent"))
    stage_complete = handoff_value(parsed, "Routing", "Stage complete").lower()
    blockers = (parsed.get("sections") or {}).get("Blockers", "")
    return {
        "previous_agent": previous,
        "next_agent": next_agent,
        "stage_complete": stage_complete,
        "blockers": blockers,
        "fallback": fallback_for(previous or next_agent, policy),
    }


def fallback_for(agent: str, policy: dict[str, Any]) -> str:
    order = policy.get("agent_order") or {}
    entry = order.get(normalize_agent(agent)) or {}
    return normalize_agent(entry.get("fallback", "")) or "planner"
