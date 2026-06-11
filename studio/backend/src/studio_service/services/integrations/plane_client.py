"""Read-only Plane REST proxy for Studio integrations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from studio_service.api.errors import StudioApiError
from studio_service.services.integrations.env import (
    load_dotenv,
    parse_card,
    plane_api_key,
    plane_base_url,
    plane_project_id,
    plane_workspace,
)


def _require_plane() -> tuple[str, str, str, str]:
    api_key = plane_api_key()
    if not api_key:
        raise StudioApiError(
            503,
            "PLANE_NOT_CONFIGURED",
            "Plane integration not configured",
            details={"env": "PLANE_API_KEY"},
        )
    return api_key, plane_workspace(), plane_project_id(), plane_base_url()


def _plane_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def _plane_card_url(workspace: str, label: str) -> str:
    return f"https://app.plane.so/{workspace}/browse/{label}/"


class PlaneIntegrationClient:
    def __init__(self, repo_root) -> None:
        self._repo_root = repo_root

    def _bootstrap(self) -> tuple[str, str, str, str]:
        load_dotenv(self._repo_root)
        return _require_plane()

    def find_issue_uuid(
        self,
        api_key: str,
        workspace: str,
        project_id: str,
        base_url: str,
        sequence_id: int,
        *,
        client: httpx.Client | None = None,
    ) -> str:
        url = f"{base_url}/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
        owns_client = client is None
        http = client or httpx.Client(timeout=30.0)
        try:
            resp = http.get(url, headers=_plane_headers(api_key), params={"per_page": 100})
            if resp.status_code >= 500:
                raise StudioApiError(
                    502,
                    "PLANE_UPSTREAM_ERROR",
                    "Plane API request failed",
                    details={"status": resp.status_code},
                )
            resp.raise_for_status()
            for item in resp.json().get("results", []):
                if item.get("sequence_id") == sequence_id:
                    return item["id"]
        finally:
            if owns_client:
                http.close()
        raise StudioApiError(404, "PLANE_CARD_NOT_FOUND", f"Card INVES-{sequence_id} not found")

    def get_card_detail(self, card: str) -> dict[str, Any]:
        try:
            label, seq = parse_card(card)
        except ValueError as exc:
            raise StudioApiError(422, "INVALID_CARD", str(exc)) from exc

        api_key, workspace, project_id, base_url = self._bootstrap()
        with httpx.Client(timeout=30.0) as http:
            issue_uuid = self.find_issue_uuid(
                api_key, workspace, project_id, base_url, seq, client=http
            )
            url = (
                f"{base_url}/api/v1/workspaces/{workspace}/projects/"
                f"{project_id}/issues/{issue_uuid}/"
            )
            resp = http.get(url, headers=_plane_headers(api_key))
            if resp.status_code == 404:
                raise StudioApiError(404, "PLANE_CARD_NOT_FOUND", f"Card {label} not found")
            if resp.status_code >= 500:
                raise StudioApiError(
                    502,
                    "PLANE_UPSTREAM_ERROR",
                    "Plane API request failed",
                    details={"status": resp.status_code},
                )
            resp.raise_for_status()
            issue = resp.json()

        state_detail = issue.get("state_detail") or {}
        parent = issue.get("parent")
        parent_label = None
        if parent:
            parent_label = self._parent_label(api_key, workspace, project_id, base_url, parent)

        description_html = issue.get("description_html") or ""
        return {
            "card": label,
            "sequence_id": seq,
            "issue_id": issue_uuid,
            "name": issue.get("name"),
            "state": {
                "id": issue.get("state"),
                "name": state_detail.get("name"),
                "group": state_detail.get("group"),
            },
            "parent": parent_label,
            "priority": issue.get("priority"),
            "description_present": bool(description_html.strip()),
            "description_html_length": len(description_html),
            "plane_url": _plane_card_url(workspace, label),
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    def _parent_label(
        self,
        api_key: str,
        workspace: str,
        project_id: str,
        base_url: str,
        parent_uuid: str,
    ) -> str | None:
        url = (
            f"{base_url}/api/v1/workspaces/{workspace}/projects/"
            f"{project_id}/issues/{parent_uuid}/"
        )
        with httpx.Client(timeout=30.0) as http:
            resp = http.get(url, headers=_plane_headers(api_key))
            if resp.status_code != 200:
                return None
            seq = resp.json().get("sequence_id")
            return f"INVES-{seq}" if seq is not None else None

    def list_epic_children(self, card: str) -> dict[str, Any]:
        try:
            label, seq = parse_card(card)
        except ValueError as exc:
            raise StudioApiError(422, "INVALID_CARD", str(exc)) from exc

        api_key, workspace, project_id, base_url = self._bootstrap()
        with httpx.Client(timeout=30.0) as http:
            epic_uuid = self.find_issue_uuid(
                api_key, workspace, project_id, base_url, seq, client=http
            )
            url = f"{base_url}/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
            resp = http.get(url, headers=_plane_headers(api_key), params={"per_page": 100})
            if resp.status_code >= 500:
                raise StudioApiError(
                    502,
                    "PLANE_UPSTREAM_ERROR",
                    "Plane API request failed",
                    details={"status": resp.status_code},
                )
            resp.raise_for_status()
            children_by_state: dict[str, list[dict[str, Any]]] = {}
            total = 0
            for item in resp.json().get("results", []):
                if item.get("parent") != epic_uuid:
                    continue
                child_seq = item.get("sequence_id")
                if child_seq is None:
                    continue
                state_name = (item.get("state_detail") or {}).get("name") or "unknown"
                entry = {
                    "card": f"INVES-{child_seq}",
                    "sequence_id": child_seq,
                    "issue_id": item.get("id"),
                    "name": item.get("name"),
                    "state": {
                        "id": item.get("state"),
                        "name": state_name,
                        "group": (item.get("state_detail") or {}).get("group"),
                    },
                }
                children_by_state.setdefault(state_name, []).append(entry)
                total += 1

        for items in children_by_state.values():
            items.sort(key=lambda x: x["sequence_id"])

        return {
            "epic": label,
            "epic_issue_id": epic_uuid,
            "children_by_state": children_by_state,
            "total": total,
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    def list_work_feed(self, limit: int = 15) -> dict[str, Any]:
        """Recent Plane issues sorted by updated_at (workboard context for dashboard)."""
        api_key, workspace, project_id, base_url = self._bootstrap()
        capped = max(1, min(limit, 50))
        url = f"{base_url}/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
        with httpx.Client(timeout=30.0) as http:
            resp = http.get(url, headers=_plane_headers(api_key), params={"per_page": 100})
            if resp.status_code >= 500:
                raise StudioApiError(
                    502,
                    "PLANE_UPSTREAM_ERROR",
                    "Plane API request failed",
                    details={"status": resp.status_code},
                )
            resp.raise_for_status()
            raw = resp.json().get("results", [])

        items: list[dict[str, Any]] = []
        for issue in raw:
            seq = issue.get("sequence_id")
            if seq is None:
                continue
            state_detail = issue.get("state_detail") or {}
            label = f"INVES-{seq}"
            items.append(
                {
                    "card": label,
                    "sequence_id": seq,
                    "issue_id": issue.get("id"),
                    "name": issue.get("name"),
                    "state": {
                        "id": issue.get("state"),
                        "name": state_detail.get("name"),
                        "group": state_detail.get("group"),
                    },
                    "priority": issue.get("priority"),
                    "parent": issue.get("parent"),
                    "updated_at": issue.get("updated_at") or issue.get("created_at"),
                    "plane_url": _plane_card_url(workspace, label),
                }
            )

        items.sort(key=lambda row: row.get("updated_at") or "", reverse=True)
        items = items[:capped]

        return {
            "items": items,
            "count": len(items),
            "fetched_at": datetime.now(UTC).isoformat(),
        }
