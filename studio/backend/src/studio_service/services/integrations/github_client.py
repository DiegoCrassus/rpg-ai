"""Read-only GitHub REST proxy for Studio integrations."""

from __future__ import annotations

from studio_service.time_utils import UTC, datetime
from typing import Any

import httpx

from studio_service.api.errors import StudioApiError
from studio_service.services.integrations.env import (
    GITHUB_API,
    github_repository,
    github_token,
    load_dotenv,
)


def _require_github(repo_root) -> tuple[str, str]:
    token = github_token(repo_root)
    if not token:
        raise StudioApiError(
            503,
            "GITHUB_NOT_CONFIGURED",
            "GitHub integration not configured",
            details={
                "env": "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC or GITHUB_PERSONAL_ACCESS_TOKEN"
            },
        )
    return token, github_repository(repo_root)


def _gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


class GitHubIntegrationClient:
    def __init__(self, repo_root) -> None:
        self._repo_root = repo_root

    def _bootstrap(self) -> tuple[str, str]:
        load_dotenv(self._repo_root)
        token = github_token(self._repo_root)
        if not token:
            raise StudioApiError(
                503,
                "GITHUB_NOT_CONFIGURED",
                "GitHub integration not configured",
                details={
                    "env": "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC or GITHUB_PERSONAL_ACCESS_TOKEN"
                },
            )
        return token, github_repository(self._repo_root)

    def list_open_pulls(self, *, base: str = "develop", state: str = "open") -> dict[str, Any]:
        token, repo = self._bootstrap()
        owner, _ = repo.split("/", 1)
        url = f"{GITHUB_API}/repos/{repo}/pulls"
        with httpx.Client(timeout=30.0) as http:
            resp = http.get(
                url,
                headers=_gh_headers(token),
                params={"state": state, "base": base, "per_page": 30, "sort": "updated"},
            )
            if resp.status_code in (401, 403):
                raise StudioApiError(
                    502,
                    "GITHUB_AUTH_ERROR",
                    "GitHub API rejected credentials",
                    details={"status": resp.status_code},
                )
            if resp.status_code >= 500:
                raise StudioApiError(
                    502,
                    "GITHUB_UPSTREAM_ERROR",
                    "GitHub API request failed",
                    details={"status": resp.status_code},
                )
            resp.raise_for_status()
            raw_pulls = resp.json()

        pulls = []
        for pr in raw_pulls:
            head = pr.get("head") or {}
            base_ref = pr.get("base") or {}
            pulls.append(
                {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "draft": pr.get("draft", False),
                    "head": {"ref": head.get("ref"), "sha": head.get("sha")},
                    "base": {"ref": base_ref.get("ref"), "sha": base_ref.get("sha")},
                    "html_url": pr.get("html_url"),
                    "user": (pr.get("user") or {}).get("login"),
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                }
            )

        return {
            "repository": repo,
            "owner": owner,
            "base": base,
            "state_filter": state,
            "pulls": pulls,
            "count": len(pulls),
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    def checks_for_ref(self, ref: str) -> dict[str, Any]:
        ref = ref.strip()
        if not ref:
            raise StudioApiError(422, "INVALID_REF", "Query parameter ref is required")

        token, repo = self._bootstrap()
        with httpx.Client(timeout=30.0) as http:
            commit = self._resolve_commit(http, token, repo, ref)
            sha = commit["sha"]
            status = self._combined_status(http, token, repo, sha)
            runs = self._workflow_runs(http, token, repo, ref)

        return {
            "repository": repo,
            "ref": ref,
            "commit": {
                "sha": sha,
                "message": (commit.get("commit") or {}).get("message"),
                "combined_status": status.get("state"),
                "statuses": status.get("statuses", []),
            },
            "workflow_runs": runs,
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    def _resolve_commit(
        self, http: httpx.Client, token: str, repo: str, ref: str
    ) -> dict[str, Any]:
        url = f"{GITHUB_API}/repos/{repo}/commits/{ref}"
        resp = http.get(url, headers=_gh_headers(token))
        if resp.status_code == 404:
            raise StudioApiError(404, "GITHUB_REF_NOT_FOUND", f"Ref not found: {ref!r}")
        if resp.status_code >= 500:
            raise StudioApiError(
                502,
                "GITHUB_UPSTREAM_ERROR",
                "GitHub API request failed",
                details={"status": resp.status_code},
            )
        resp.raise_for_status()
        return resp.json()

    def _combined_status(
        self, http: httpx.Client, token: str, repo: str, sha: str
    ) -> dict[str, Any]:
        url = f"{GITHUB_API}/repos/{repo}/commits/{sha}/status"
        resp = http.get(url, headers=_gh_headers(token))
        if resp.status_code == 404:
            return {"state": None, "statuses": []}
        resp.raise_for_status()
        body = resp.json()
        statuses = [
            {
                "context": s.get("context"),
                "state": s.get("state"),
                "description": s.get("description"),
                "target_url": s.get("target_url"),
            }
            for s in body.get("statuses", [])
        ]
        return {"state": body.get("state"), "statuses": statuses}

    def _workflow_runs(
        self, http: httpx.Client, token: str, repo: str, branch: str
    ) -> list[dict[str, Any]]:
        url = f"{GITHUB_API}/repos/{repo}/actions/runs"
        resp = http.get(
            url,
            headers=_gh_headers(token),
            params={"branch": branch, "per_page": 10},
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return [
            {
                "id": run.get("id"),
                "name": run.get("name"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "event": run.get("event"),
                "html_url": run.get("html_url"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
            }
            for run in resp.json().get("workflow_runs", [])
        ]
