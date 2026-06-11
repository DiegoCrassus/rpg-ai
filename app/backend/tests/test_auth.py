"""Auth JWT tests."""


import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_sync_creates_user(client: AsyncClient, master_headers: dict):
    response = await client.post("/api/v1/auth/sync", headers=master_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "master@example.com"
    assert data["status"] == "active"
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_auth_me_requires_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "auth_required"


@pytest.mark.asyncio
async def test_auth_me_returns_profile(client: AsyncClient, master_headers: dict):
    await client.post("/api/v1/auth/sync", headers=master_headers)
    response = await client.get("/api/v1/auth/me", headers=master_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "master@example.com"


@pytest.mark.asyncio
async def test_invalid_jwt_rejected(client: AsyncClient):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
