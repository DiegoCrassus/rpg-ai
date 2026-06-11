#!/usr/bin/env python3
"""Cursor hooks — token budget tracking and hard limits."""

from __future__ import annotations

import argparse
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

from sdlc_gateway_lib import read_payload  # noqa: E402
from token_budget import (  # noqa: E402
    check_allow_action,
    load_config,
    record_usage,
    reset_session,
    status_text,
)


def _allow(extra: str = "") -> None:
    out: dict = {"permission": "allow"}
    if extra:
        out["agent_message"] = extra
    print(json.dumps(out))
    sys.exit(0)


def _deny(user: str, agent: str) -> None:
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": user,
                "agent_message": agent,
            }
        )
    )
    sys.exit(0)


def cmd_session_start(_payload: dict) -> None:
    reset_session(REPO)
    cfg = load_config(REPO)
    _allow(f"token session reset. cap={cfg.session_budget} enforce={cfg.enforce}")


def cmd_after_response(payload: dict) -> None:
    ledger = record_usage(payload, event="after-response", root=REPO)
    cfg = load_config(REPO)
    msg = f"tokens total={ledger.total_tokens}/{cfg.session_budget}"
    if ledger.blocked and cfg.enforce == "strict":
        msg += f" BLOCKED: {ledger.block_reason}"
    _allow(msg)


def cmd_after_thought(payload: dict) -> None:
    record_usage(payload, event="after-thought", root=REPO)
    _allow()


def cmd_subagent_start(_payload: dict) -> None:
    ok, msg, ledger = check_allow_action("subagent-start", root=REPO)
    cfg = load_config(REPO)
    if not ok and cfg.enforce == "strict" and cfg.block_task_on_exceed:
        _deny(
            "Token budget exceeded — subagent blocked.",
            f"BUDGET BLOCK. {msg}. Run: python3 .sdlc/scripts/token_budget_status.py reset",
        )
    _allow(msg if msg.startswith("WARN") else f"subagent ok. total={ledger.total_tokens}")


def cmd_subagent_stop(payload: dict) -> None:
    record_usage(payload, event="subagent-stop", root=REPO)
    _allow()


def cmd_before_prompt(payload: dict) -> None:
    ok, msg, ledger = check_allow_action("before-prompt", root=REPO)
    cfg = load_config(REPO)
    record_usage(payload, event="before-prompt", root=REPO)
    if not ok and cfg.enforce == "strict" and cfg.block_prompt_on_exceed:
        _deny(
            "Token budget exceeded — reset budget before continuing.",
            f"BUDGET BLOCK. {msg}. total={ledger.total_tokens}",
        )
    _allow(msg if msg.startswith("WARN") else "")


def cmd_stop(_payload: dict) -> None:
    print(status_text(REPO), file=sys.stderr)
    _allow()


def main() -> None:
    parser = argparse.ArgumentParser(description="SDLC token budget hook")
    parser.add_argument(
        "mode",
        choices=[
            "session-start",
            "after-response",
            "after-thought",
            "subagent-start",
            "subagent-stop",
            "before-prompt",
            "stop",
        ],
    )
    args = parser.parse_args()
    try:
        payload = read_payload()
        handlers = {
        "session-start": cmd_session_start,
        "after-response": cmd_after_response,
        "after-thought": cmd_after_thought,
        "subagent-start": cmd_subagent_start,
        "subagent-stop": cmd_subagent_stop,
        "before-prompt": cmd_before_prompt,
        "stop": cmd_stop,
        }
        handlers[args.mode](payload)
    except SystemExit:
        raise
    except Exception as exc:
        _deny(
            "Token budget hook internal error — interaction blocked.",
            f"{type(exc).__name__}: {exc}",
        )


if __name__ == "__main__":
    main()
