from __future__ import annotations

from fastapi import APIRouter

from studio_service.deps import RepoRoot
from studio_service.services.session_reader import read_handoff, read_session_gate

router = APIRouter(prefix="/session", tags=["s1-shell"])


@router.get("/gate")
def session_gate(repo_root: RepoRoot) -> dict:
    return read_session_gate(repo_root)


@router.get("/handoff")
def session_handoff(repo_root: RepoRoot) -> dict:
    return read_handoff(repo_root)
