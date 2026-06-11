"""Invite accept and expiry tests."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from rpg_platform.auth.jwt import create_test_token
from rpg_platform.db.models import Invite


@pytest.mark.asyncio
async def test_invite_accept_email_match(client: AsyncClient):
    master_id = uuid.uuid4()
    player_id = uuid.uuid4()
    master_headers = {"Authorization": f"Bearer {create_test_token(str(master_id), 'master@example.com')}"}
    player_headers = {"Authorization": f"Bearer {create_test_token(str(player_id), 'player@example.com')}"}

    await client.post("/api/v1/auth/sync", headers=master_headers)
    await client.post("/api/v1/auth/sync", headers=player_headers)

    create = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Invite Mesa", "rpg_system": "dnd5e"},
    )
    mesa_id = create.json()["id"]

    invite_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/invites",
        headers=master_headers,
        json={"email": "player@example.com"},
    )
    assert invite_resp.status_code == 201
    token = invite_resp.json()["token"]

    accept = await client.post("/api/v1/invites/accept", headers=player_headers, json={"token": token})
    assert accept.status_code == 200
    assert accept.json()["mesa_id"] == mesa_id
    assert accept.json()["role"] == "player"

    reuse = await client.post("/api/v1/invites/accept", headers=player_headers, json={"token": token})
    assert reuse.status_code == 409


@pytest.mark.asyncio
async def test_invite_expired(client: AsyncClient, session_factory):
    master_id = uuid.uuid4()
    player_id = uuid.uuid4()
    master_headers = {"Authorization": f"Bearer {create_test_token(str(master_id), 'master@example.com')}"}
    player_headers = {"Authorization": f"Bearer {create_test_token(str(player_id), 'player@example.com')}"}

    await client.post("/api/v1/auth/sync", headers=master_headers)
    await client.post("/api/v1/auth/sync", headers=player_headers)

    create = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Expired Invite Mesa", "rpg_system": "dnd5e"},
    )
    mesa_id = create.json()["id"]

    invite_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/invites",
        headers=master_headers,
        json={"email": "player@example.com"},
    )
    invite_id = uuid.UUID(invite_resp.json()["id"])
    token = invite_resp.json()["token"]

    async with session_factory() as session:
        invite = await session.get(Invite, invite_id)
        assert invite is not None
        invite.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        await session.commit()

    response = await client.post(
        "/api/v1/invites/accept",
        headers=player_headers,
        json={"token": token},
    )
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "invite_expired"
