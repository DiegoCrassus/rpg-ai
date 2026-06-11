"""Request bodies for S5 registry / validation / simulation endpoints."""

from __future__ import annotations

from pydantic import Field

from studio_service.schemas.common import OptionalRootBody


class ValidationRunBody(OptionalRootBody):
    pass


class DoctorRunBody(OptionalRootBody):
    pass


class SimulationPreviewBody(OptionalRootBody):
    scenario: str | None = None
    intent: str | None = None
    path_label: str | None = None
    step_kind: str | None = None
    tag: str | None = None


class WorkflowAssistanceBody(OptionalRootBody):
    kind: str | None = Field(
        default=None,
        description="validation_gap | missing_source_ref | workflow_handoff | plane_follow_up_draft | risk_summary",
    )
