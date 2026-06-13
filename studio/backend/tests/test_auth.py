"""Studio optional Bearer auth (RPG-92 AC-1)."""

from __future__ import annotations

from studio_service.config import get_settings


def test_studio_routes_open_without_auth_token(client) -> None:
    response = client.get("/studio/health")
    assert response.status_code == 200


def test_studio_routes_require_bearer_when_token_set(client, monkeypatch) -> None:
    monkeypatch.setenv("STUDIO_AUTH_TOKEN", "local-dev-secret")
    get_settings.cache_clear()
    try:
        denied = client.get("/studio/health")
        assert denied.status_code == 401
        assert denied.json()["error"]["code"] == "UNAUTHORIZED"

        ok = client.get(
            "/studio/health",
            headers={"Authorization": "Bearer local-dev-secret"},
        )
        assert ok.status_code == 200
    finally:
        monkeypatch.delenv("STUDIO_AUTH_TOKEN", raising=False)
        get_settings.cache_clear()
