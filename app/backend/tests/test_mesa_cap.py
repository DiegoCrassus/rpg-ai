"""Mesa master cap tests (BR-01)."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.auth.jwt import create_test_token


@pytest.mark.asyncio
async def test_master_cap_blocks_third_mesa(client: AsyncClient):
    user_id = uuid.uuid4()
    headers = {
        "Authorization": f"Bearer {create_test_token(str(user_id), 'cap@example.com')}"
    }
    await client.post("/api/v1/auth/sync", headers=headers)

    for i in range(2):
        response = await client.post(
            "/api/v1/mesas",
            headers=headers,
            json={"name": f"Mesa {i}", "rpg_system": "dnd5e"},
        )
        assert response.status_code == 201

    third = await client.post(
        "/api/v1/mesas",
        headers=headers,
        json={"name": "Mesa 3", "rpg_system": "dnd5e"},
    )
    assert third.status_code == 409
    assert third.json()["error"]["code"] == "master_cap_exceeded"
