"""Schemas for SDLC learning loop events."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    BUGFIX = "bugfix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    SDLC_META = "sdlc_meta"
    INFRA = "infra"
    HOTFIX = "hotfix"
    READONLY = "readonly"
    UNKNOWN = "unknown"


class TaskOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


INTENT_TO_TASK_TYPE: dict[str, TaskType] = {
    "BUGFIX": TaskType.BUGFIX,
    "FEATURE": TaskType.FEATURE,
    "GREENFIELD": TaskType.FEATURE,
    "SDLC_META": TaskType.SDLC_META,
    "DOCS_ONLY": TaskType.DOCS,
    "INFRA": TaskType.INFRA,
    "HOTFIX": TaskType.HOTFIX,
    "READONLY": TaskType.READONLY,
}


def intent_to_task_type(intent: str) -> TaskType:
    return INTENT_TO_TASK_TYPE.get((intent or "").upper(), TaskType.UNKNOWN)


@dataclass
class SDLCRunEvent:
    """One agent task execution record."""

    task_id: str
    card: str
    task_type: str
    agent: str
    stage: str
    branch: str = ""
    model: str | None = None
    prompt_version: str | None = None
    tools_called: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: int = 0
    tests_pass: int | None = None
    tests_fail: int | None = None
    lint_exit: int | None = None
    typecheck_exit: int | None = None
    doctor_exit: int | None = None
    security_exit: int | None = None
    rework_count: int = 0
    outcome: str = TaskOutcome.PARTIAL.value
    human_feedback: str | None = None
    reviewer_verdict: str | None = None
    rollback: bool = False
    requirement_adherence: float | None = None
    files_changed: int | None = None
    reward: float = 0.0
    lesson: str | None = None
    ts: str = ""
    session_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SDLCRunEvent:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)
