"""Journey 1 integration: create mesa → import → approve → invite."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.agents.sheet_import.runner import run_import_job
from rpg_platform.auth.jwt import create_test_token
from rpg_platform.db.session import get_session_factory


@pytest.mark.asyncio
async def test_journey1_create_import_approve_invite(client: AsyncClient):
    master_id = uuid.uuid4()
    player_id = uuid.uuid4()
    master_headers = {"Authorization": f"Bearer {create_test_token(str(master_id), 'journey-master@example.com')}"}
    player_headers = {"Authorization": f"Bearer {create_test_token(str(player_id), 'journey-player@example.com')}"}

    await client.post("/api/v1/auth/sync", headers=master_headers)
    await client.post("/api/v1/auth/sync", headers=player_headers)

    mesa_resp = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Journey Mesa", "rpg_system": "D&D 5e", "description": "Integration test"},
    )
    assert mesa_resp.status_code == 201
    mesa = mesa_resp.json()
    assert mesa["status"] == "importing"
    mesa_id = mesa["id"]

    upload = await client.post(
        f"/api/v1/mesas/{mesa_id}/import",
        headers=master_headers,
        files={"file": ("char.pdf", b"%PDF-1.4 test", "application/pdf")},
    )
    assert upload.status_code == 202
    job_id = uuid.UUID(upload.json()["id"])

    factory = get_session_factory()
    async with factory() as session:
        await run_import_job(session, job_id)
        await session.commit()

    approve = await client.post(f"/api/v1/mesas/{mesa_id}/import/approve", headers=master_headers)
    assert approve.status_code == 200
    assert approve.json()["mesa_status"] == "active"

    templates = await client.get(f"/api/v1/mesas/{mesa_id}/templates", headers=master_headers)
    assert templates.status_code == 200
    assert len(templates.json()) >= 1

    invite = await client.post(
        f"/api/v1/mesas/{mesa_id}/invites",
        headers=master_headers,
        json={"email": "journey-player@example.com"},
    )
    assert invite.status_code == 201
    token = invite.json()["token"]

    accept = await client.post("/api/v1/invites/accept", headers=player_headers, json={"token": token})
    assert accept.status_code == 200

    participants = await client.get(f"/api/v1/mesas/{mesa_id}/participants", headers=master_headers)
    assert participants.status_code == 200
    roles = {p["role"] for p in participants.json()}
    assert "master" in roles
    assert "player" in roles

    health = await client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
