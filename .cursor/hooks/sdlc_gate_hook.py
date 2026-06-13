#!/usr/bin/env python3
"""Cursor preToolUse — deny Write only on protected paths when gate is closed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DSL = REPO / ".sdlc" / "dsl"
HOOKS = Path(__file__).resolve().parent

if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

try:
    import gate as _gate  # noqa: E402
except Exception as _gate_exc:
    _GATE_LOAD_FAILED = _gate_exc
else:
    _GATE_LOAD_FAILED = None

from sdlc_gateway_lib import (  # noqa: E402
    emit_studio_event,
    enforce_orchestrator_delegation_write,
    extract_write_path,
    read_payload,
    require_policy,
)


def _allow() -> None:
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)


def _deny(user: str, agent: str) -> None:
    print(json.dumps({"permission": "deny", "user_message": user, "agent_message": agent}))
    sys.exit(0)


def main() -> None:
    if _GATE_LOAD_FAILED is not None:
        _deny(
            "SDLC gate module failed to load — write blocked.",
            f"Fix .sdlc/dsl/gate.py import error: {_GATE_LOAD_FAILED}",
        )

    if _gate.is_gate_enforcement_off(REPO):
        _allow()

    payload = read_payload()
    rel = extract_write_path(payload)
    if not rel:
        _allow()

    policy = require_policy()
    enforce_orchestrator_delegation_write(rel, policy)

    config = _gate.load_gate_config(REPO)
    if not _gate.is_protected(rel, config):
        _allow()

    ok, msg = _gate.check_write(rel, REPO)
    if ok:
        emit_studio_event(
            "gate.write_allowed",
            "sdlc_gate_hook",
            {"path": rel, "tool": "Write"},
            category="gate",
        )
        _allow()

    card = _gate.load_session_gate(REPO).card or "RPG-N"
    emit_studio_event(
        "gate.write_denied",
        "sdlc_gate_hook",
        {"path": rel, "reason": msg, "card_required": card},
        category="gate",
    )
    _deny(
        "SDLC gate: write blocked on protected path.",
        (
            f"Blocked '{rel}'. {msg} "
            f"Run: python3 .sdlc/dsl/cli.py workflow start --card {card} --stage implementation"
        ),
    )


if __name__ == "__main__":
    main()
