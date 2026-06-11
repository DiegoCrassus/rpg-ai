"""Derive live SDLC session context when the formal gate is closed but work is in flight."""

from __future__ import annotations

import re
import subprocess
from studio_service.time_utils import UTC, datetime
from pathlib import Path
from typing import Any

_CARD_PREFIX_CACHE: dict[str, re.Pattern[str]] = {}
_EMPTY_MARKERS = frozenset({"", "—", "-", "none", "n/a"})

_AGENT_PRIMARY_STAGE: dict[str, str] = {
    "intent-analyst": "ticket",
    "planner": "ticket",
    "architect": "architecture",
    "implementer": "implementation",
    "qa": "validation",
    "reviewer": "review",
    "devops": "deployment",
    "auto-fixer": "autofix",
    "migration-runner": "implementation",
}

_INACTIVE_AGENTS = frozenset(
    {
        "",
        "none",
        "orchestrator",
        "workflow-classify",
        "intent analyst",
    }
)

_RECENT_ACTIVITY_SECONDS = 4 * 60 * 60


def _card_re(repo_root: Path) -> re.Pattern[str]:
    key = str(repo_root.resolve())
    if key not in _CARD_PREFIX_CACHE:
        from studio_service.services.integrations.env import card_prefix

        prefix = re.escape(card_prefix(repo_root))
        _CARD_PREFIX_CACHE[key] = re.compile(rf"{prefix}-\d+", re.IGNORECASE)
    return _CARD_PREFIX_CACHE[key]


def enrich_session(
    repo_root: Path,
    gate: dict[str, Any],
    handoff_sections: dict[str, dict[str, str]],
    *,
    recent_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Merge gate, handoff, git branch, and observability into a dashboard session view."""

    routing = handoff_sections.get("Routing", {})
    handoff_session = handoff_sections.get("Session", {})

    gate_open = gate.get("gate_status") == "open"
    gate_card = _clean(gate.get("card"), repo_root)
    gate_branch = _clean(gate.get("branch"), repo_root)
    gate_stage = _clean(gate.get("stage"), repo_root)
    handoff_card = _clean(handoff_session.get("Card"), repo_root)
    handoff_branch = _clean(handoff_session.get("Branch"), repo_root)
    handoff_stage = _clean(handoff_session.get("Stage"), repo_root)
    handoff_matches_gate = bool(
        gate_card
        and handoff_card
        and gate_card.upper() == handoff_card.upper()
    )

    if gate_open:
        card = gate_card or handoff_card
        branch = gate_branch or handoff_branch
        stage = gate_stage or ""
        next_agent = _clean(routing.get("Next agent")) if handoff_matches_gate else None
        stage_complete = (
            _clean(routing.get("Stage complete")) if handoff_matches_gate else "no"
        )
        return {
            "gate_open": True,
            "execution_active": True,
            "live_source": "gate",
            "card": card or "",
            "branch": branch or _current_git_branch(repo_root) or "",
            "stage": stage,
            "next_agent": next_agent or "",
            "stage_complete": stage_complete or "no",
            "inferred_stage": False,
        }

    next_agent = _clean(routing.get("Next agent"), repo_root)
    stage_complete = _clean(routing.get("Stage complete"), repo_root)
    card = gate_card or handoff_card
    branch = gate_branch or handoff_branch
    stage = gate_stage
    live_source = None
    inferred_stage = False

    if not branch:
        branch = _current_git_branch(repo_root)
    if not card and branch:
        card = _card_from_branch(branch, repo_root)
    if not card or not branch:
        obs_ctx = _recent_obs_context(recent_events, repo_root)
        if obs_ctx:
            card = card or obs_ctx.get("card")
            branch = branch or obs_ctx.get("branch")
            if obs_ctx.get("active"):
                live_source = "observability"

    stage_complete_yes = (stage_complete or "").lower() == "yes"
    if not stage:
        if handoff_stage and not stage_complete_yes:
            stage = handoff_stage
        elif next_agent:
            inferred = _infer_stage(next_agent, card)
            if inferred:
                stage = inferred
                inferred_stage = True
    elif stage_complete_yes and next_agent:
        inferred = _infer_stage(next_agent, card)
        if inferred:
            stage = inferred
            inferred_stage = True

    execution_active = False
    if _agent_is_active(next_agent):
        if stage or card or branch or (live_source == "observability"):
            execution_active = True
            live_source = live_source or "handoff"

    return {
        "gate_open": False,
        "execution_active": execution_active,
        "live_source": live_source,
        "card": card or "",
        "branch": branch or "",
        "stage": stage or "",
        "next_agent": next_agent or "",
        "stage_complete": stage_complete or "",
        "inferred_stage": inferred_stage,
    }


def _clean(value: str | None, repo_root: Path) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if text.lower() in _EMPTY_MARKERS:
        return None
    if text.startswith("—") or text.startswith("-"):
        return None
    card_match = _card_re(repo_root).search(text)
    if card_match and "(" in text:
        return card_match.group(0).upper()
    return text


def _agent_is_active(agent: str | None) -> bool:
    if not agent:
        return False
    return agent.strip().lower() not in _INACTIVE_AGENTS


def _infer_stage(next_agent: str, card: str | None) -> str | None:
    slug = next_agent.strip().lower().replace("_", "-")
    if slug == "planner" and card:
        return "requirements"
    return _AGENT_PRIMARY_STAGE.get(slug)


def _card_from_branch(branch: str, repo_root: Path) -> str | None:
    match = _card_re(repo_root).search(branch)
    return match.group(0).upper() if match else None


def _current_git_branch(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def _recent_obs_context(
    events: list[dict[str, Any]] | None,
    repo_root: Path,
) -> dict[str, Any] | None:
    if not events:
        return None

    now = datetime.now(UTC)
    best: dict[str, Any] | None = None

    for event in events:
        ts = _parse_timestamp(event.get("timestamp"))
        if ts is None:
            continue
        age = (now - ts).total_seconds()
        if age > _RECENT_ACTIVITY_SECONDS:
            continue

        correlation = event.get("correlation") or {}
        card = _clean(correlation.get("card"), repo_root)
        branch = _clean(correlation.get("branch"), repo_root)
        if not card and not branch:
            continue

        ctx = {"card": card, "branch": branch, "active": True, "timestamp": event.get("timestamp")}
        if best is None:
            best = ctx
            continue
        best_ts = _parse_timestamp(best.get("timestamp"))
        if best_ts is None or ts > best_ts:
            best = ctx

    return best


def _parse_timestamp(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
