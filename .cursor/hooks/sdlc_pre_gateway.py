#!/usr/bin/env python3
"""Pre-interaction SDLC gateway for shell and subagent starts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from sdlc_gateway_lib import (
    allow,
    deny,
    extract_command,
    extract_subagent,
    read_payload,
    require_policy,
    routing,
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

    if requested == expected:
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
    payload = read_payload()
    policy = require_policy()

    deny_unsafe_shell(extract_command(payload), policy)

    # Pipeline routing applies only when gate enforcement is strict.
    if not gate_enforcement_off():
        enforce_next_subagent(payload, policy)

    allow()


if __name__ == "__main__":
    main()
