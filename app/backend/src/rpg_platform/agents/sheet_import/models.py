"""Sheet import agent models."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateFieldProposal(BaseModel):
    key: str
    type: str
    label: str
    required: bool | None = None
    order: int | None = None
    children: list[TemplateFieldProposal] | None = None


class TemplateProposal(BaseModel):
    name: str
    slug: str
    description: str | None = None
    fields: list[TemplateFieldProposal]


class CharacterProposal(BaseModel):
    character_name: str
    values: dict[str, Any] = Field(default_factory=dict)
    extraction_confidence: float = 0.0


class FieldConfidence(BaseModel):
    key: str
    confidence: float
    source_region: str | None = None


class ImportProposal(BaseModel):
    job_id: UUID
    detected_system: str
    detection_confidence: float
    source_pages: int = 1
    template_proposal: TemplateProposal
    character_proposal: CharacterProposal | None = None
    field_confidence: list[FieldConfidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_review: bool = True

    def to_contract_dict(self) -> dict[str, Any]:
        data = self.model_dump(mode="json", exclude_none=True)
        data["requires_review"] = True
        return data
