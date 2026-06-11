"""OpenAPI models for S2 canvas endpoints (React Flow consumer)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ValidationStatus = Literal["pass", "warn", "fail", "not_run"]


class SourceRef(BaseModel):
    ref_type: str
    ref: str
    summary: str | None = None


class ValidationOverlaySummary(BaseModel):
    id: str
    status: ValidationStatus
    check_type: str
    message_count: int
    source_refs: list[SourceRef]


class CanvasNode(BaseModel):
    id: str
    graph_node_id: str
    label: str
    type: str
    category: str
    source_refs: list[SourceRef]
    annotations: list[dict[str, str]] = Field(default_factory=list)
    validation_overlays: list[ValidationOverlaySummary] = Field(default_factory=list)


class CanvasEdge(BaseModel):
    id: str
    graph_edge_id: str
    source: str
    target: str
    relation: str
    source_refs: list[SourceRef]
    validation_overlays: list[ValidationOverlaySummary] = Field(default_factory=list)
    label: str | None = None
    summary: str | None = None
    agent: str | None = None
    skill: str | None = None


class CanvasOverlay(BaseModel):
    id: str
    validation_ref: str
    target: dict[str, str]
    check_type: str
    status: ValidationStatus
    messages: list[dict[str, Any]]
    source_refs: list[SourceRef]


class CanvasSection(BaseModel):
    id: str
    report_ref: str
    kind: str
    title: str
    status: str
    summary: str
    items: list[dict[str, Any]]
    source_refs: list[SourceRef]


class CanvasLegendCategory(BaseModel):
    id: str
    label: str


class CanvasLegend(BaseModel):
    categories: list[CanvasLegendCategory]
    validation_statuses: dict[str, int]


class CanvasFilters(BaseModel):
    section: str | None = None
    validation_status: ValidationStatus | None = None
    entity_type: str | None = None
    q: str | None = None


class CanvasMeta(BaseModel):
    total_nodes: int
    filtered_nodes: int
    total_edges: int
    filtered_edges: int


class CanvasFullResponse(BaseModel):
    """Stable S2 payload for React Flow mapViewModel.ts."""

    canvas: dict[str, Any]
    nodes: list[CanvasNode]
    edges: list[CanvasEdge]
    overlays: list[CanvasOverlay]
    sections: list[CanvasSection]
    legend: CanvasLegend
    filters: CanvasFilters
    meta: CanvasMeta


class CanvasNodeDetailResponse(BaseModel):
    node: CanvasNode
    overlays: list[CanvasOverlay]
