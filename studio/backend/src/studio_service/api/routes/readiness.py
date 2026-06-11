from __future__ import annotations

from fastapi import APIRouter

from studio_service.deps import EngineSvc, RepoRoot

router = APIRouter(tags=["s1-shell"])


@router.get("/readiness")
def readiness(repo_root: RepoRoot, engine: EngineSvc) -> dict:
    return engine.readiness(repo_root)
