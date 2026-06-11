"""Request bodies for S6 evidence projection endpoints."""

from __future__ import annotations

from pydantic import Field

from studio_service.schemas.common import OptionalRootBody


class EvidenceDraftBody(OptionalRootBody):
    card: str | None = Field(default=None, description="Plane card id (INVES-N)")
    title: str | None = Field(default=None, description="Evidence title override")
    branch: str | None = Field(default=None, description="Feature branch for artifacts.branch")
