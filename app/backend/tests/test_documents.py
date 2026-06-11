"""Document visibility policy tests."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.auth.jwt import create_test_token
from rpg_platform.db.enums import DocumentType, DocumentVisibility


@pytest.mark.asyncio
async def test_master_only_hidden_from_player(client: AsyncClient):
    master_id = uuid.uuid4()
    player_id = uuid.uuid4()
    master_headers = {"Authorization": f"Bearer {create_test_token(str(master_id), 'master@example.com')}"}
    player_headers = {"Authorization": f"Bearer {create_test_token(str(player_id), 'player@example.com')}"}

    await client.post("/api/v1/auth/sync", headers=master_headers)
    await client.post("/api/v1/auth/sync", headers=player_headers)

    mesa = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Doc Mesa", "rpg_system": "dnd5e"},
    )
    mesa_id = mesa.json()["id"]

    await client.post(f"/api/v1/mesas/{mesa_id}/import/seed", headers=master_headers)

    secret = await client.post(
        f"/api/v1/mesas/{mesa_id}/documents",
        headers=master_headers,
        json={
            "title": "Secret Lore",
            "type": DocumentType.LORE.value,
            "visibility": DocumentVisibility.MASTER_ONLY.value,
        },
    )
    assert secret.status_code == 201
    doc_id = secret.json()["id"]

    invite = await client.post(
        f"/api/v1/mesas/{mesa_id}/invites",
        headers=master_headers,
        json={"email": "player@example.com"},
    )
    await client.post(
        "/api/v1/invites/accept",
        headers=player_headers,
        json={"token": invite.json()["token"]},
    )

    player_list = await client.get(f"/api/v1/mesas/{mesa_id}/documents", headers=player_headers)
    assert player_list.status_code == 200
    assert all(d["id"] != doc_id for d in player_list.json())

    player_get = await client.get(
        f"/api/v1/mesas/{mesa_id}/documents/{doc_id}",
        headers=player_headers,
    )
    assert player_get.status_code == 403

    master_get = await client.get(
        f"/api/v1/mesas/{mesa_id}/documents/{doc_id}",
        headers=master_headers,
    )
    assert master_get.status_code == 200
