"""Sheet import flow with mocked agent."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.agents.sheet_import.runner import run_import_job
from rpg_platform.db.enums import ImportJobStatus
from rpg_platform.db.session import get_session_factory


@pytest.mark.asyncio
async def test_import_flow_mock_agent(client: AsyncClient, master_headers: dict):
    await client.post("/api/v1/auth/sync", headers=master_headers)
    create_resp = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Import Mesa", "rpg_system": "dnd5e"},
    )
    mesa_id = create_resp.json()["id"]

    files = {"file": ("sheet.png", b"\x89PNG\r\n\x1a\n", "image/png")}
    import_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/import",
        headers=master_headers,
        files=files,
    )
    assert import_resp.status_code == 202
    job_id = uuid.UUID(import_resp.json()["id"])

    factory = get_session_factory()
    async with factory() as session:
        await run_import_job(session, job_id)
        await session.commit()

    status_resp = await client.get(f"/api/v1/mesas/{mesa_id}/import", headers=master_headers)
    assert status_resp.status_code == 200
    job = status_resp.json()
    assert job["status"] == ImportJobStatus.PROPOSED.value
    assert job["proposal"] is not None
    assert job["proposal"]["detected_system"] == "dnd5e_2024"

    approve_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/import/approve",
        headers=master_headers,
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["mesa_status"] == "active"

    mesa_resp = await client.get(f"/api/v1/mesas/{mesa_id}", headers=master_headers)
    assert mesa_resp.json()["status"] == "active"
