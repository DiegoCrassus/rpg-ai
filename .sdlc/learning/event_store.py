"""Append-only task-level event store for SDLC learning loop."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc

try:
    from .reward_engine import RewardEngine, RewardInput
    from .schemas import SDLCRunEvent, TaskOutcome, intent_to_task_type
except ImportError:
    from reward_engine import RewardEngine, RewardInput  # type: ignore[no-redef]
    from schemas import SDLCRunEvent, TaskOutcome, intent_to_task_type  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVENTS_PATH = ROOT / ".sdlc" / "learning" / "data" / "events.jsonl"
MAX_LINES = 2000


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def events_path(root: Path | None = None) -> Path:
    root = root or ROOT
    return root / ".sdlc" / "learning" / "data" / "events.jsonl"


def read_lines(path: Path | None = None) -> list[str]:
    path = path or DEFAULT_EVENTS_PATH
    if not path.is_file():
        return []
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def read_events(path: Path | None = None) -> list[SDLCRunEvent]:
    events: list[SDLCRunEvent] = []
    for line in read_lines(path):
        try:
            events.append(SDLCRunEvent.from_dict(json.loads(line)))
        except (json.JSONDecodeError, TypeError):
            continue
    return events


def prune(max_lines: int = MAX_LINES, path: Path | None = None) -> int:
    path = path or DEFAULT_EVENTS_PATH
    lines = read_lines(path)
    if len(lines) <= max_lines:
        return 0
    kept = lines[-max_lines:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return len(lines) - max_lines


def append_event(event: SDLCRunEvent, *, root: Path | None = None, max_lines: int = MAX_LINES) -> Path:
    root = root or ROOT
    path = events_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not event.ts:
        event.ts = _now_iso()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
    prune(max_lines, path)
    return path


def record_task(
    *,
    card: str,
    agent: str,
    stage: str,
    intent: str = "",
    branch: str = "",
    model: str | None = None,
    duration_ms: int = 0,
    tokens_in: int = 0,
    tokens_out: int = 0,
    tools_called: list[str] | None = None,
    tests_pass: int | None = None,
    tests_fail: int | None = None,
    lint_exit: int | None = None,
    doctor_exit: int | None = None,
    security_exit: int | None = None,
    rework_count: int = 0,
    gateway_block: bool = False,
    reviewer_verdict: str | None = None,
    human_feedback: str | None = None,
    session_id: str = "",
    root: Path | None = None,
) -> SDLCRunEvent:
    engine = RewardEngine()
    reward, outcome = engine.compute(
        RewardInput(
            tests_fail=tests_fail or 0,
            tests_pass=tests_pass,
            lint_exit=lint_exit,
            doctor_exit=doctor_exit,
            security_exit=security_exit,
            rework_count=rework_count,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tools_total=len(tools_called or []),
            gateway_block=gateway_block,
            human_approved=(reviewer_verdict or "").upper() == "APPROVE",
            human_escalated=(reviewer_verdict or "").upper() == "ESCALATE",
        )
    )
    lesson = _lesson_from_outcome(agent, stage, outcome, reward)
    event = SDLCRunEvent(
        task_id=str(uuid.uuid4()),
        card=card,
        task_type=intent_to_task_type(intent).value,
        agent=agent,
        stage=stage,
        branch=branch,
        model=model,
        tools_called=tools_called or [],
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        duration_ms=duration_ms,
        tests_pass=tests_pass,
        tests_fail=tests_fail,
        lint_exit=lint_exit,
        doctor_exit=doctor_exit,
        security_exit=security_exit,
        rework_count=rework_count,
        outcome=outcome.value,
        human_feedback=human_feedback,
        reviewer_verdict=reviewer_verdict,
        reward=reward,
        lesson=lesson,
        ts=_now_iso(),
        session_id=session_id,
    )
    append_event(event, root=root)
    return event


def _lesson_from_outcome(agent: str, stage: str, outcome: TaskOutcome, reward: float) -> str:
    if reward >= 0.8:
        return f"{stage}/{agent}: ok — keep procedure"
    if outcome == TaskOutcome.FAILURE:
        return f"{stage}/{agent}: fail — rerun tests before handoff yes"
    return f"{stage}/{agent}: partial — check evidence before next agent"


def tail(n: int = 20, path: Path | None = None) -> list[SDLCRunEvent]:
    return read_events(path)[-n:]


def events_for_card(card: str, path: Path | None = None) -> list[SDLCRunEvent]:
    return [e for e in read_events(path) if e.card == card]


def status_text(path: Path | None = None) -> str:
    events = read_events(path)
    lines = [
        f"learning_events: {events_path()}",
        f"count: {len(events)}",
    ]
    if events:
        last = events[-1]
        lines.append(
            f"last: {last.agent}@{last.stage} reward={last.reward} outcome={last.outcome}"
        )
    return "\n".join(lines)


def load_qa_metrics(card: str, root: Path | None = None) -> dict[str, Any]:
    root = root or ROOT
    path = root / ".sdlc" / "memory" / f"qa-evidence-{card}.json"
    alt = root / ".sdlc" / "memory" / f".qa-evidence-{card}.json"
    for candidate in (path, alt):
        if candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
    return {}
