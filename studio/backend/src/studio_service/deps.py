"""FastAPI dependencies."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import Depends

from studio_service.api.errors import StudioApiError
from studio_service.config import Settings, get_settings
from studio_service.services.engine import EngineService


def resolve_repo_root(override: str | None, settings: Settings | None = None) -> Path:
    if override:
        path = Path(override).expanduser().resolve()
        if not (path / ".sdlc/sdlc.yaml").is_file():
            raise StudioApiError(400, "INVALID_REPO_ROOT", f"Not an SDLC repo root: {path}")
        return path
    cfg = settings or get_settings()
    return cfg.resolved_repo_root


def get_default_repo_root(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Path:
    return settings.resolved_repo_root


def get_engine() -> EngineService:
    return EngineService()


RepoRoot = Annotated[Path, Depends(get_default_repo_root)]
EngineSvc = Annotated[EngineService, Depends(get_engine)]
