#!/usr/bin/env python3
"""Pre-interaction SDLC gateway for shell and subagent starts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from sdlc_gateway_lib import (
    allow,
    deny,
    enforce_orchestrator_delegation_shell,
    extract_command,
    extract_subagent,
    normalize_agent,
    read_payload,
    require_policy,
    routing,
    set_active_subagent,
)

REPO = Path(__file__).resolve().parents[2]
DSL = REPO / ".sdlc" / "dsl"

if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

try:
    import gate as _gate  # noqa: E402
except ImportError:
    _gate = None  # type: ignore[assignment]


def gate_enforcement_off() -> bool:
    if _gate is None:
        return False
    return _gate.is_gate_enforcement_off(REPO)


def deny_unsafe_shell(command: str, policy: dict) -> None:
    if not command:
        return
    pre_policy = policy.get("pre_gateway") or {}
    for pattern in pre_policy.get("deny_shell_patterns") or []:
        if re.search(pattern, command):
            deny(
                pre_policy.get(
                    "deny_message",
                    "Deterministic SDLC gateway blocked this shell command.",
                ),
                (
                    "The command matched a deterministic deny pattern "
                    f"({pattern!r}). Return to the previous SDLC step and use the "
                    "approved workflow instead."
                ),
                event_type="gateway.shell_denied",
                event_payload={"command": command, "matcher": pattern},
            )


def mark_subagent_start(payload: dict, policy: dict) -> None:
    """Track active pipeline subagent for orchestrator-delegation enforcement."""
    requested = extract_subagent(payload)
    if not requested:
        return
    generic_agents = {"explore", "generalpurpose", "general-purpose", "shell"}
    if requested in generic_agents:
        return
    valid = {normalize_agent(str(a)) for a in (policy.get("valid_agents") or [])}
    pipeline = {
        normalize_agent(str(a))
        for a in ((policy.get("orchestrator_delegation") or {}).get("pipeline_agents") or [])
    }
    if requested in valid and requested in pipeline:
        set_active_subagent(requested)


def enforce_next_subagent(payload: dict, policy: dict) -> None:
    requested = extract_subagent(payload)
    if not requested:
        return

    valid_agents = set(policy.get("valid_agents") or [])
    generic_agents = {"explore", "generalpurpose", "general-purpose", "shell"}
    if requested not in valid_agents and requested not in generic_agents:
        return

    current = routing(policy)
    expected = current.get("next_agent", "")
    if not expected or expected == "none":
        return

    # Exploration and generic agents are allowed when they are only gathering context.
    if requested in generic_agents:
        return

    support_agents = {
        normalize_agent(str(a)) for a in (policy.get("support_agents") or [])
    }
    if requested in support_agents:
        return

    if requested == expected:
        mark_subagent_start(payload, policy)
        return

    deny(
        "SDLC gateway: subagent does not match the current handoff route.",
        (
            f"The handoff expects '{expected}', but this interaction requested "
            f"'{requested}'. Read `.sdlc/memory/orchestrator-handoff.md` and "
            "return to the routed step before continuing."
        ),
        event_type="gateway.subagent_start",
        event_payload={
            "subagent_type": requested,
            "expected_agent": expected,
            "allowed": False,
        },
    )


def main() -> None:
    try:
        payload = read_payload()
        policy = require_policy()
        command = extract_command(payload)

        deny_unsafe_shell(command, policy)

        # Pipeline routing applies only when gate enforcement is strict.
        if not gate_enforcement_off():
            enforce_next_subagent(payload, policy)
            enforce_orchestrator_delegation_shell(command, policy)

        allow()
    except SystemExit:
        raise
    except Exception as exc:
        deny(
            "SDLC gateway internal error — interaction blocked.",
            f"{type(exc).__name__}: {exc}",
        )


if __name__ == "__main__":
    main()
