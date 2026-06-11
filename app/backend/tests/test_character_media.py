"""Character sheet media upload tests."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.auth.jwt import create_test_token


async def _setup_mesa_with_character(
    client: AsyncClient,
    master_headers: dict[str, str],
) -> tuple[str, str]:
    await client.post("/api/v1/auth/sync", headers=master_headers)

    mesa_resp = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Media Mesa", "rpg_system": "dnd5e"},
    )
    assert mesa_resp.status_code == 201
    mesa_id = mesa_resp.json()["id"]

    await client.post(f"/api/v1/mesas/{mesa_id}/import/seed", headers=master_headers)

    templates = await client.get(f"/api/v1/mesas/{mesa_id}/templates", headers=master_headers)
    template_id = templates.json()[0]["id"]

    char_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/characters",
        headers=master_headers,
        json={
            "template_id": template_id,
            "character_name": "Media Hero",
        },
    )
    assert char_resp.status_code == 201
    return mesa_id, char_resp.json()["id"]


@pytest.mark.asyncio
async def test_upload_media_success_as_master(client: AsyncClient, master_headers: dict):
    mesa_id, character_id = await _setup_mesa_with_character(client, master_headers)

    response = await client.post(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/media",
        headers=master_headers,
        data={"field_key": "portrait"},
        files={"file": ("portrait.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["storage_path"] == f"characters/{character_id}/media/portrait.png"
    assert body["signed_url"]


@pytest.mark.asyncio
async def test_upload_media_forbidden_for_non_owner_player(client: AsyncClient):
    master_id = uuid.uuid4()
    player_id = uuid.uuid4()
    master_headers = {"Authorization": f"Bearer {create_test_token(str(master_id), 'master@example.com')}"}
    player_headers = {"Authorization": f"Bearer {create_test_token(str(player_id), 'player@example.com')}"}

    await client.post("/api/v1/auth/sync", headers=master_headers)
    await client.post("/api/v1/auth/sync", headers=player_headers)

    mesa_id, character_id = await _setup_mesa_with_character(client, master_headers)

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

    response = await client.post(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/media",
        headers=player_headers,
        data={"field_key": "portrait"},
        files={"file": ("portrait.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "character_forbidden"


@pytest.mark.asyncio
async def test_upload_media_rejects_invalid_field_key(client: AsyncClient, master_headers: dict):
    mesa_id, character_id = await _setup_mesa_with_character(client, master_headers)

    response = await client.post(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/media",
        headers=master_headers,
        data={"field_key": "../traversal"},
        files={"file": ("portrait.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_field_key"
