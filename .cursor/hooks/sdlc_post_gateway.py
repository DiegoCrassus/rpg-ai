#!/usr/bin/env python3
"""Post-interaction SDLC gateway for deterministic handoff validation."""

from __future__ import annotations

import json
import sys

from sdlc_gateway_lib import (
    emit_studio_event,
    fallback_for,
    handoff_value,
    normalize_agent,
    parse_handoff,
    read_handoff,
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


def followup(agent: str, reason: str, details: list[str]) -> None:
    route = normalize_agent(agent) or "planner"
    detail_text = "\n".join(f"- {item}" for item in details) if details else "- unspecified"
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
    sys.exit(0)


def main() -> None:
    # Read and ignore the event payload for now; the repository handoff is the
    # deterministic source for routing after subagents stop.
    sys.stdin.read()

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
        except Exception as exc:
            followup(previous, "handoff evidence verifier error", [str(exc)])

    sys.exit(0)


if __name__ == "__main__":
    main()
