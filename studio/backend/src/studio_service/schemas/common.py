"""Shared request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptionalRootBody(BaseModel):
    root: str | None = Field(default=None, description="Repository root override")
