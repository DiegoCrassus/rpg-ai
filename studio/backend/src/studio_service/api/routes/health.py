from __future__ import annotations

from fastapi import APIRouter

from studio_service.config import get_settings
from studio_service.deps import RepoRoot

router = APIRouter(tags=["s1-shell"])


@router.get("/health")
def health(repo_root: RepoRoot) -> dict:
    settings = get_settings()
    marker = repo_root / ".sdlc/sdlc.yaml"
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.version,
        "repo_root": str(repo_root),
        "repo_root_reachable": marker.is_file(),
    }
