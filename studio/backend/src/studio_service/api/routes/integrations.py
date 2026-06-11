"""S6 — read-only Plane and GitHub integration routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from studio_service.deps import RepoRoot
from studio_service.services.integrations.github_client import GitHubIntegrationClient
from studio_service.services.integrations.plane_client import PlaneIntegrationClient

router = APIRouter(prefix="/integrations", tags=["s6-integrations"])


@router.get("/plane/cards/{card}")
def plane_card_detail(card: str, repo_root: RepoRoot) -> dict:
    return PlaneIntegrationClient(repo_root).get_card_detail(card)


@router.get("/plane/epics/{card}/children")
def plane_epic_children(card: str, repo_root: RepoRoot) -> dict:
    return PlaneIntegrationClient(repo_root).list_epic_children(card)


@router.get("/plane/feed")
def plane_work_feed(
    repo_root: RepoRoot,
    limit: Annotated[int, Query(ge=1, le=50, description="Max recent issues")] = 15,
) -> dict:
    return PlaneIntegrationClient(repo_root).list_work_feed(limit=limit)


@router.get("/github/pulls")
def github_pulls(
    repo_root: RepoRoot,
    base: Annotated[str, Query(description="Base branch filter")] = "develop",
    state: Annotated[str, Query(description="PR state filter")] = "open",
) -> dict:
    return GitHubIntegrationClient(repo_root).list_open_pulls(base=base, state=state)


@router.get("/github/checks")
def github_checks(
    repo_root: RepoRoot,
    ref: Annotated[str, Query(description="Branch name or commit SHA")],
) -> dict:
    return GitHubIntegrationClient(repo_root).checks_for_ref(ref)
