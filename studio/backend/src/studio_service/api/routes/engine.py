from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from studio_service.config import Settings, get_settings
from studio_service.deps import EngineSvc, RepoRoot, resolve_repo_root
from studio_service.schemas.common import OptionalRootBody

router = APIRouter(prefix="/engine", tags=["s1-engine"])


@router.post("/compile")
def engine_compile(
    body: OptionalRootBody,
    engine: EngineSvc,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    root = resolve_repo_root(body.root, settings)
    return engine.compile(root)


@router.post("/validate")
def engine_validate(
    body: OptionalRootBody,
    engine: EngineSvc,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    root = resolve_repo_root(body.root, settings)
    return engine.validate(root)


@router.get("/canvas")
def engine_canvas_get(
    engine: EngineSvc,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None),
) -> dict:
    target = resolve_repo_root(root, settings) if root else repo_root
    return engine.canvas(target)
