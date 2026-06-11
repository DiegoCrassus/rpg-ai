"""Read-only config file browse for Studio builders (no writes)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from studio_service.deps import RepoRoot
from studio_service.schemas.config import ConfigFileContentResponse, ConfigFileListResponse
from studio_service.services.config_browse import list_config_files, read_config_file

router = APIRouter(prefix="/config", tags=["s5-config"])


@router.get("/files", response_model=ConfigFileListResponse)
def config_list_files(
    repo_root: RepoRoot,
    kind: str = Query(..., description="agent | rule | skill | command"),
    q: str | None = Query(default=None, description="Filter by path or filename"),
) -> ConfigFileListResponse:
    return list_config_files(repo_root, kind, q=q)


@router.get("/file", response_model=ConfigFileContentResponse)
def config_read_file(
    repo_root: RepoRoot,
    path: str = Query(..., description="Repo-relative allowlisted path"),
) -> ConfigFileContentResponse:
    return read_config_file(repo_root, path)
