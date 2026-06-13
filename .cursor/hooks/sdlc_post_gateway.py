#!/usr/bin/env python3
"""Post-interaction SDLC gateway for deterministic handoff validation."""

from __future__ import annotations

import json
import sys

from sdlc_gateway_lib import (
    allow,
    clear_active_subagent,
    emit_studio_event,
    fallback_for,
    handoff_value,
    normalize_agent,
    parse_handoff,
    read_handoff,
    read_payload,
    require_policy,
    routing,
    validate_handoff,
)


def blockers_are_clear(blockers: str) -> bool:
    lines = [line.strip(" -\t").strip().lower() for line in blockers.splitlines()]
    meaningful = [line for line in lines if line]
    if not meaningful:
        return True
    clear_values = {"none", "no", "n/a", "na", "—", "-"}
    return all(
        line in clear_values
        or line.startswith("none for ")
        or line.startswith("no blockers")
        or line.startswith("no blocker")
        for line in meaningful
    )


def _mark_gateway_block() -> None:
    try:
        from pathlib import Path

        repo = Path(__file__).resolve().parents[2]
        gate_path = repo / ".sdlc" / "memory" / "session-gate.json"
        if not gate_path.is_file():
            return
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        if not isinstance(gate, dict):
            return
        meta = dict(gate.get("meta") or {})
        meta["last_gateway_block"] = True
        gate["meta"] = meta
        gate_path.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    except Exception:
        return


def _ledger_append(
    event_type: str,
    *,
    reason: str = "",
    details: list[str] | None = None,
    evidence_verified: bool | None = None,
) -> None:
    try:
        import sys
        from pathlib import Path

        repo = Path(__file__).resolve().parents[2]
        scripts = repo / ".sdlc" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from execution_ledger import append_from_gateway  # noqa: PLC0415

        append_from_gateway(
            event_type,
            reason=reason,
            details=details,
            evidence_verified=evidence_verified,
        )
    except Exception:
        return


def followup(agent: str, reason: str, details: list[str]) -> None:
    route = normalize_agent(agent) or "planner"
    detail_text = "\n".join(f"- {item}" for item in details) if details else "- unspecified"
    _mark_gateway_block()
    _ledger_append("gateway_block", reason=reason, details=details)
    emit_studio_event(
        "gateway.handoff_blocked",
        "sdlc_post_gateway",
        {
            "next_agent": route,
            "blockers": details or [reason],
            "reason": reason,
        },
        category="gateway",
    )
    message = f"""SDLC deterministic gateway blocked stage advancement.

Return to `{route}` before continuing.

Reason: {reason}

Details:
{detail_text}

Required action:
- Re-run or resume `{route}` with the current `.sdlc/memory/orchestrator-handoff.md`.
- Fix the missing evidence or blocker.
- Write a complete Markdown handoff before advancing again.
"""
    print(json.dumps({"followup_message": message}))
    clear_active_subagent()
    sys.exit(0)


def main() -> None:
    try:
        _run_main()
    except SystemExit:
        raise
    except Exception as exc:
        followup(
            "planner",
            "post-gateway internal error",
            [f"{type(exc).__name__}: {exc}"],
        )


def _run_main() -> None:
    read_payload()

    policy = require_policy()

    problems = validate_handoff(policy)
    route = routing(policy)
    previous = route.get("previous_agent") or "planner"
    next_agent = route.get("next_agent") or ""

    if problems:
        followup(
            previous or fallback_for(next_agent, policy),
            "handoff contract is incomplete",
            problems,
        )

    parsed = parse_handoff(read_handoff())
    stage_complete = handoff_value(parsed, "Routing", "Stage complete").lower()
    blockers = (parsed.get("sections") or {}).get("Blockers", "")

    if (
        (policy.get("post_gateway") or {}).get("reroute_on_incomplete_stage", True)
        and stage_complete == "no"
    ):
        target = next_agent if next_agent and next_agent != "none" else previous
        followup(
            target,
            "stage is explicitly incomplete",
            ["Routing.Stage complete is `no`"],
        )

    if (
        (policy.get("post_gateway") or {}).get("reroute_on_blockers", True)
        and not blockers_are_clear(blockers)
    ):
        target = next_agent if next_agent and next_agent != "none" else fallback_for(previous, policy)
        followup(
            target,
            "handoff contains unresolved blockers",
            [line for line in blockers.splitlines() if line.strip()],
        )

    evidence_verified: bool | None = None
    if stage_complete == "yes" and (policy.get("post_gateway") or {}).get(
        "verify_handoff_evidence", True
    ):
        try:
            import subprocess
            from pathlib import Path

            repo = Path(__file__).resolve().parents[2]
            script = repo / ".sdlc" / "scripts" / "handoff_evidence_verify.py"
            if script.is_file():
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    cwd=repo,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    detail = (proc.stderr or proc.stdout or "verification failed").strip()
                    followup(
                        previous or "qa",
                        "handoff evidence verification failed",
                        detail.splitlines()[:8],
                    )
                else:
                    evidence_verified = True
        except Exception as exc:
            followup(previous, "handoff evidence verifier error", [str(exc)])

    if stage_complete == "yes":
        _ledger_append(
            "stage_complete",
            reason="stage marked complete",
            evidence_verified=evidence_verified,
        )
    clear_active_subagent()
    allow()


if __name__ == "__main__":
    main()
