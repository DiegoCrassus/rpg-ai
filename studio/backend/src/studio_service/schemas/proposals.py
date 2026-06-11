"""S4 propose-only mutation API models (ADR-010 / INVES-84)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ProposalKind = Literal["workflow", "agent", "rule", "skill", "command"]
ProposalOp = Literal["replace_block", "insert_after", "delete_lines", "create_file"]
GateStage = Literal["planning", "architecture", "sdlc_meta"]
DryRunStep = Literal["validate", "doctor", "gateway-check"]
AuthorityBadge = Literal["proposed_non_authoritative"]


class StructuredOp(BaseModel):
    op: ProposalOp
    path: str
    anchor: str | None = None
    content: str | None = None


class SimulatedGate(BaseModel):
    stage: GateStage
    card: str = Field(min_length=1)


class ProposalCreateRequest(BaseModel):
    kind: ProposalKind
    title: str = Field(min_length=1)
    target_paths: list[str] = Field(min_length=1)
    ops: list[StructuredOp] = Field(min_length=1)
    simulated_gate: SimulatedGate


class DryRunResult(BaseModel):
    proposal_id: str
    step: DryRunStep
    exit_code: Literal[0, 1]
    summary: str
    details: list[dict] = Field(default_factory=list)


class GatewayPathResult(BaseModel):
    path: str
    allowed: bool
    reason: str
    gate_status: str
    stage: str


class ProposalResponse(BaseModel):
    proposal_id: str
    kind: ProposalKind
    title: str
    target_paths: list[str]
    patch_format: Literal["unified_diff"] = "unified_diff"
    patch_body: str
    authority_badge: AuthorityBadge = "proposed_non_authoritative"
    simulated_gate: SimulatedGate
    created_at: str
    dry_runs: dict[str, DryRunResult] = Field(default_factory=dict)
