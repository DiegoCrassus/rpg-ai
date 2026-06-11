"""Read-only config file browse schemas (S5 config builders)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ConfigKind = Literal["agent", "rule", "skill", "command"]


class ConfigFileEntry(BaseModel):
    path: str
    name: str
    size_bytes: int | None = None


class ConfigFileListResponse(BaseModel):
    kind: ConfigKind
    files: list[ConfigFileEntry]
    q: str | None = None


class ConfigFileContentResponse(BaseModel):
    path: str
    content: str
    exists: bool = True
