from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest
from studio_service.services.integrations import env as integration_env


def _mock_response(status_code: int, json_body: object) -> httpx.Response:
    request = httpx.Request("GET", "https://integration.test/")
    return httpx.Response(status_code, json=json_body, request=request)


@pytest.fixture
def no_plane_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PLANE_API_KEY", raising=False)
    monkeypatch.setattr(integration_env, "load_dotenv", lambda _root: None)
    monkeypatch.setattr(integration_env, "plane_api_key", lambda: None)
    monkeypatch.setattr(
        "studio_service.services.integrations.plane_client.load_dotenv",
        lambda _root: None,
    )
    monkeypatch.setattr(
        "studio_service.services.integrations.plane_client.plane_api_key",
        lambda: None,
    )


@pytest.fixture
def no_github_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC", raising=False)
    monkeypatch.delenv("GITHUB_PERSONAL_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setattr(integration_env, "load_dotenv", lambda _root: None)
    monkeypatch.setattr(integration_env, "github_token", lambda: None)
    monkeypatch.setattr(
        "studio_service.services.integrations.github_client.load_dotenv",
        lambda _root: None,
    )
    monkeypatch.setattr(
        "studio_service.services.integrations.github_client.github_token",
        lambda: None,
    )


def test_plane_card_missing_api_key(client, no_plane_key) -> None:
    response = client.get("/studio/integrations/plane/cards/RPG-90")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "PLANE_NOT_CONFIGURED"
    assert "not configured" in body["error"]["message"].lower()


def test_plane_epic_children_missing_api_key(client, no_plane_key) -> None:
    response = client.get("/studio/integrations/plane/epics/RPG-76/children")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PLANE_NOT_CONFIGURED"


def test_plane_invalid_card(client, no_plane_key) -> None:
    response = client.get("/studio/integrations/plane/cards/BAD-1")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_CARD"


def test_github_pulls_missing_token(client, no_github_token) -> None:
    response = client.get("/studio/integrations/github/pulls")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "GITHUB_NOT_CONFIGURED"


def test_github_checks_missing_token(client, no_github_token) -> None:
    response = client.get("/studio/integrations/github/checks", params={"ref": "develop"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "GITHUB_NOT_CONFIGURED"


def test_github_checks_requires_ref(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC", "gh_test")
    response = client.get("/studio/integrations/github/checks")
    assert response.status_code == 422


def test_plane_card_detail_success(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLANE_API_KEY", "plane_test")
    monkeypatch.setenv("PLANE_WORKSPACE_SLUG", "rpg")
    monkeypatch.setenv("PLANE_PROJECT_ID", "proj-uuid")

    list_response = _mock_response(
        200,
        {
            "results": [
                {"id": "issue-uuid-90", "sequence_id": 90, "name": "Integration API"},
            ]
        },
    )
    detail_response = _mock_response(
        200,
        {
            "id": "issue-uuid-90",
            "sequence_id": 90,
            "name": "Integration API",
            "state": "state-1",
            "state_detail": {"name": "In Progress", "group": "started"},
            "description_html": "<p>AC</p>",
            "parent": None,
            "priority": "medium",
        },
    )

    mock_http = MagicMock()
    mock_http.get.side_effect = [list_response, detail_response]

    with patch("studio_service.services.integrations.plane_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http
        response = client.get("/studio/integrations/plane/cards/RPG-90")

    assert response.status_code == 200
    body = response.json()
    assert body["card"] == "RPG-90"
    assert body["name"] == "Integration API"
    assert body["state"]["name"] == "In Progress"
    assert body["description_present"] is True
    assert "rpg/browse/RPG-90" in body["plane_url"]


def test_plane_epic_children_grouped(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLANE_API_KEY", "plane_test")

    list_responses = [
        _mock_response(200, {"results": [{"id": "epic-uuid", "sequence_id": 76, "name": "Epic"}]}),
        _mock_response(
            200,
            {
                "results": [
                    {
                        "id": "child-1",
                        "sequence_id": 78,
                        "name": "Backend",
                        "parent": "epic-uuid",
                        "state": "s1",
                        "state_detail": {"name": "Todo", "group": "unstarted"},
                    },
                    {
                        "id": "child-2",
                        "sequence_id": 79,
                        "name": "Frontend",
                        "parent": "epic-uuid",
                        "state": "s2",
                        "state_detail": {"name": "In Progress", "group": "started"},
                    },
                    {
                        "id": "other",
                        "sequence_id": 99,
                        "name": "Unrelated",
                        "parent": None,
                        "state": "s3",
                        "state_detail": {"name": "Done", "group": "completed"},
                    },
                ]
            },
        ),
    ]

    mock_http = MagicMock()
    mock_http.get.side_effect = list_responses

    with patch("studio_service.services.integrations.plane_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http
        response = client.get("/studio/integrations/plane/epics/RPG-76/children")

    assert response.status_code == 200
    body = response.json()
    assert body["epic"] == "RPG-76"
    assert body["total"] == 2
    assert len(body["children_by_state"]["Todo"]) == 1
    assert body["children_by_state"]["Todo"][0]["card"] == "RPG-78"
    assert len(body["children_by_state"]["In Progress"]) == 1


def test_plane_work_feed_sorted(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLANE_API_KEY", "plane_test")

    feed_response = _mock_response(
        200,
        {
            "results": [
                {
                    "id": "a",
                    "sequence_id": 10,
                    "name": "Older",
                    "state": "s1",
                    "state_detail": {"name": "Done", "group": "completed"},
                    "updated_at": "2026-06-01T10:00:00Z",
                },
                {
                    "id": "b",
                    "sequence_id": 11,
                    "name": "Newer",
                    "state": "s2",
                    "state_detail": {"name": "In Progress", "group": "started"},
                    "updated_at": "2026-06-03T12:00:00Z",
                },
            ]
        },
    )

    mock_http = MagicMock()
    mock_http.get.return_value = feed_response

    with patch("studio_service.services.integrations.plane_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http
        response = client.get("/studio/integrations/plane/feed", params={"limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert body["items"][0]["card"] == "RPG-11"
    assert body["items"][0]["state"]["name"] == "In Progress"
    assert "rpg/browse/RPG-11" in body["items"][0]["plane_url"]


def test_plane_work_feed_missing_api_key(client, no_plane_key) -> None:
    response = client.get("/studio/integrations/plane/feed")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PLANE_NOT_CONFIGURED"


def test_github_pulls_success(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC", "gh_test")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/repo")

    pull_response = _mock_response(
        200,
        [
            {
                "number": 12,
                "title": "Feature",
                "state": "open",
                "draft": False,
                "head": {"ref": "feature/x", "sha": "abc"},
                "base": {"ref": "develop", "sha": "def"},
                "html_url": "https://github.com/org/repo/pull/12",
                "user": {"login": "dev"},
                "created_at": "2026-06-01T00:00:00Z",
                "updated_at": "2026-06-02T00:00:00Z",
            }
        ],
    )

    mock_http = MagicMock()
    mock_http.get.return_value = pull_response

    with patch("studio_service.services.integrations.github_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http
        response = client.get("/studio/integrations/github/pulls")

    assert response.status_code == 200
    body = response.json()
    assert body["repository"] == "org/repo"
    assert body["count"] == 1
    assert body["pulls"][0]["number"] == 12
    assert body["pulls"][0]["head"]["ref"] == "feature/x"


def test_github_checks_success(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC", "gh_test")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/repo")

    commit_response = _mock_response(200, {"sha": "sha123", "commit": {"message": "test"}})
    status_response = _mock_response(
        200,
        {"state": "success", "statuses": [{"context": "ci", "state": "success"}]},
    )
    runs_response = _mock_response(
        200,
        {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "event": "pull_request",
                    "html_url": "https://github.com/org/repo/actions/runs/1",
                    "created_at": "2026-06-01T00:00:00Z",
                    "updated_at": "2026-06-01T01:00:00Z",
                }
            ]
        },
    )

    mock_http = MagicMock()
    mock_http.get.side_effect = [commit_response, status_response, runs_response]

    with patch("studio_service.services.integrations.github_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http
        response = client.get(
            "/studio/integrations/github/checks",
            params={"ref": "feature/RPG-90-plane-github-integration-api"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["commit"]["sha"] == "sha123"
    assert body["commit"]["combined_status"] == "success"
    assert len(body["workflow_runs"]) == 1
    assert body["workflow_runs"][0]["conclusion"] == "success"
