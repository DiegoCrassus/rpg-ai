"""Settings and CORS configuration tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from rpg_platform.api.deps import get_db
from rpg_platform.config import Settings, get_settings
from rpg_platform.main import create_app
from sqlalchemy.ext.asyncio import AsyncSession


def test_default_cors_origins_include_loopback_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    get_settings.cache_clear()
    settings = Settings(_env_file=None)
    origins = settings.cors_origin_list
    assert "http://127.0.0.1:5173" in origins
    assert "http://localhost:5173" in origins


@pytest.mark.asyncio
async def test_cors_preflight_allows_127_0_0_1(
    monkeypatch: pytest.MonkeyPatch,
    session_factory,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    get_settings.cache_clear()

    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/mesas",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"
