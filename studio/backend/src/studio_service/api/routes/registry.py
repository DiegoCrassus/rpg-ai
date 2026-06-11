"""S5 registry graph API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from studio_service.config import Settings, get_settings
from studio_service.deps import RepoRoot, resolve_repo_root
from studio_service.services.foundation_views import build_registry_graph

router = APIRouter(prefix="/registry", tags=["s5-registry"])


@router.get("/graph")
def registry_graph(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None, description="Repository root override"),
) -> dict:
    target = resolve_repo_root(root, settings) if root else repo_root
    return build_registry_graph(target)
