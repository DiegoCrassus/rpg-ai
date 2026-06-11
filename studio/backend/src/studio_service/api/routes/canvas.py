from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Response
from fastapi.responses import JSONResponse

from studio_service.config import Settings, get_settings
from studio_service.deps import EngineSvc, RepoRoot, resolve_repo_root
from studio_service.schemas.canvas import CanvasFullResponse, CanvasNodeDetailResponse
from studio_service.services.canvas import apply_canvas_filters, canvas_etag, node_detail
from studio_service.services.workflow_builder_canvas import build_workflow_builder_canvas

router = APIRouter(prefix="/canvas", tags=["s2-canvas"])


@router.get("/workflow-builder", response_model=CanvasFullResponse)
def canvas_workflow_builder(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None, description="Repository root override"),
) -> dict:
    """Lifecycle stages and workflow transitions for the propose-only builder."""

    target = resolve_repo_root(root, settings) if root else repo_root
    return build_workflow_builder_canvas(target)


@router.get("/full", response_model=CanvasFullResponse)
def canvas_full(
    engine: EngineSvc,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None, description="Repository root override"),
    section: str | None = Query(default=None, description="Filter nodes by category (e.g. sdlc, cursor)"),
    validation_status: str | None = Query(
        default=None,
        description="Filter nodes/overlays by validation status (pass, warn, fail, not_run)",
    ),
    entity_type: str | None = Query(default=None, description="Filter nodes by graph entity type (e.g. stage, agent)"),
    q: str | None = Query(default=None, description="Case-insensitive search across label, ids, and source refs"),
) -> dict:
    target = resolve_repo_root(root, settings) if root else repo_root
    raw = engine.canvas(target)
    return apply_canvas_filters(
        raw,
        section=section,
        validation_status=validation_status,
        entity_type=entity_type,
        q=q,
    )


@router.get("", response_model=CanvasFullResponse)
def canvas_get(
    response: Response,
    engine: EngineSvc,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None),
    section: str | None = Query(default=None),
    validation_status: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    q: str | None = Query(default=None),
    if_none_match: Annotated[str | None, Header(alias="If-None-Match")] = None,
) -> dict | JSONResponse:
    target = resolve_repo_root(root, settings) if root else repo_root
    raw = engine.canvas(target)
    etag = canvas_etag(raw)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-store"
    if if_none_match and if_none_match.strip() == etag:
        return JSONResponse(status_code=304, content=None)

    payload = apply_canvas_filters(
        raw,
        section=section,
        validation_status=validation_status,
        entity_type=entity_type,
        q=q,
    )
    return payload


@router.get("/nodes/{display_id}", response_model=CanvasNodeDetailResponse)
def canvas_node_get(
    display_id: str,
    engine: EngineSvc,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
    root: str | None = Query(default=None),
) -> dict:
    target = resolve_repo_root(root, settings) if root else repo_root
    raw = engine.canvas(target)
    return node_detail(raw, display_id)
