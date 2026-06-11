"""S6 — non-executing publish evidence projection."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from studio_service.config import Settings, get_settings
from studio_service.deps import RepoRoot, resolve_repo_root
from studio_service.schemas.evidence import EvidenceDraftBody
from studio_service.services.foundation_views import build_evidence_draft

router = APIRouter(prefix="/evidence", tags=["s6-evidence"])


@router.post("/draft")
def evidence_draft(
    body: EvidenceDraftBody,
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    target = resolve_repo_root(body.root, settings) if body.root else repo_root
    return build_evidence_draft(
        target,
        card=body.card,
        title=body.title,
        branch=body.branch,
    )
