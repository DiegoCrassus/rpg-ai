"""Character sheet version snapshot tests (AC-5)."""

import uuid

import pytest
from httpx import AsyncClient
from rpg_platform.services.characters import CAMPAIGNS_BUCKET, version_snapshot_path
from rpg_platform.services.storage import StorageService


@pytest.mark.asyncio
async def test_v1_snapshot_retrievable_after_v2_write(
    client: AsyncClient,
    master_headers: dict,
):
    await client.post("/api/v1/auth/sync", headers=master_headers)

    mesa_resp = await client.post(
        "/api/v1/mesas",
        headers=master_headers,
        json={"name": "Version Mesa", "rpg_system": "dnd5e"},
    )
    mesa_id = mesa_resp.json()["id"]

    await client.post(f"/api/v1/mesas/{mesa_id}/import/seed", headers=master_headers)

    templates = await client.get(f"/api/v1/mesas/{mesa_id}/templates", headers=master_headers)
    template_id = templates.json()[0]["id"]

    char_resp = await client.post(
        f"/api/v1/mesas/{mesa_id}/characters",
        headers=master_headers,
        json={
            "template_id": template_id,
            "character_name": "Version Hero",
            "initial_values": {"level": 1},
        },
    )
    assert char_resp.status_code == 201
    character_id = char_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/data",
        headers=master_headers,
        json={"values": {"level": 2}},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["version"] == 2

    versions_resp = await client.get(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/versions",
        headers=master_headers,
    )
    assert versions_resp.status_code == 200
    versions = {v["version"]: v["storage_path"] for v in versions_resp.json()}
    v1_path = versions[1]
    assert "/versions/v1.json" in v1_path

    storage = StorageService(use_memory=True)
    v1_envelope = await storage.get_json(CAMPAIGNS_BUCKET, v1_path)
    assert v1_envelope["meta"]["entity_version"] == 1
    assert v1_envelope["payload"]["values"]["level"] == 1

    current = await client.get(
        f"/api/v1/mesas/{mesa_id}/characters/{character_id}/data",
        headers=master_headers,
    )
    assert current.json()["meta"]["entity_version"] == 2
    assert current.json()["payload"]["values"]["level"] == 2

    expected_v1 = version_snapshot_path(uuid.UUID(mesa_id), uuid.UUID(character_id), 1)
    assert v1_path == expected_v1
