"""StudioEvent envelope and timeline response models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

EventCategory = Literal["gateway", "obs", "handoff", "gate"]


class EventCorrelation(BaseModel):
    run_id: str | None = None
    card: str | None = None
    branch: str | None = None
    session_id: str | None = None


class StudioEvent(BaseModel):
    schema_version: str = Field(default="1.0")
    event_id: str
    event_type: str
    category: EventCategory
    timestamp: str
    source: str
    correlation_id: str = ""
    correlation: EventCorrelation = Field(default_factory=EventCorrelation)
    payload: dict[str, Any] = Field(default_factory=dict)


class TimelineResponse(BaseModel):
    events: list[StudioEvent]
    count: int


class ObsRunsResponse(BaseModel):
    runs: list[dict[str, Any]]
    count: int


class ObsMetricsResponse(BaseModel):
    kpis: dict[str, Any]
    summary: list[dict[str, Any]]
