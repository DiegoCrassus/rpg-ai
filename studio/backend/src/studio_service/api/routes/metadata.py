from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from studio_service.config import Settings, get_settings
from studio_service.deps import RepoRoot, resolve_repo_root
from studio_service.services.pipeline_metadata import build_pipeline_metadata

router = APIRouter(prefix="/metadata", tags=["authoring-metadata"])


@router.get("/pipeline")
def metadata_pipeline(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None, description="Repository root override"),
) -> dict:
    """Lifecycle stages and pipeline agents/skills for builders and dropdowns."""

    target = resolve_repo_root(root, settings) if root else repo_root
    return build_pipeline_metadata(target)
