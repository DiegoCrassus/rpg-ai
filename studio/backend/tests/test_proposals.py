from __future__ import annotations

import pytest
from studio_service.services.mutation import reset_proposal_store_for_tests


@pytest.fixture(autouse=True)
def _clear_proposals() -> None:
    reset_proposal_store_for_tests()
    yield
    reset_proposal_store_for_tests()


def _proposal_payload() -> dict:
    return {
        "kind": "command",
        "title": "INVES-86 test command",
        "target_paths": [".cursor/commands/test-inves86-proposal.md"],
        "ops": [
            {
                "op": "create_file",
                "path": ".cursor/commands/test-inves86-proposal.md",
                "content": "# INVES-86 proposal test\n",
            }
        ],
        "simulated_gate": {"stage": "sdlc_meta", "card": "INVES-86"},
    }


def test_create_get_delete_proposal_lifecycle(client) -> None:
    created = client.post("/studio/proposals", json=_proposal_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["authority_badge"] == "proposed_non_authoritative"
    assert body["patch_format"] == "unified_diff"
    assert "+++ b/.cursor/commands/test-inves86-proposal.md" in body["patch_body"]
    proposal_id = body["proposal_id"]

    fetched = client.get(f"/studio/proposals/{proposal_id}")
    assert fetched.status_code == 200
    assert fetched.json()["proposal_id"] == proposal_id

    deleted = client.delete(f"/studio/proposals/{proposal_id}")
    assert deleted.status_code == 204
    assert client.get(f"/studio/proposals/{proposal_id}").status_code == 404


def test_create_rejects_forbidden_path(client) -> None:
    payload = _proposal_payload()
    payload["target_paths"] = [".sdlc/memory/evil.md"]
    payload["ops"][0]["path"] = ".sdlc/memory/evil.md"
    response = client.post("/studio/proposals", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "path_not_allowed"


def test_apply_route_not_registered(client) -> None:
    openapi = client.get("/openapi.json").json()
    paths = openapi.get("paths", {})
    assert not any("/apply" in path for path in paths)


def test_validate_dry_run(client) -> None:
    proposal_id = client.post("/studio/proposals", json=_proposal_payload()).json()["proposal_id"]
    response = client.post(f"/studio/proposals/{proposal_id}/validate")
    assert response.status_code == 200
    body = response.json()
    assert body["step"] == "validate"
    assert body["exit_code"] in (0, 1)
    assert body["proposal_id"] == proposal_id


def test_gateway_check_dry_run(client) -> None:
    proposal_id = client.post("/studio/proposals", json=_proposal_payload()).json()["proposal_id"]
    response = client.post(f"/studio/proposals/{proposal_id}/gateway-check")
    assert response.status_code == 200
    body = response.json()
    assert body["step"] == "gateway-check"
    assert body["exit_code"] == 0
    assert body["details"]
    assert body["details"][0]["path"] == ".cursor/commands/test-inves86-proposal.md"
    assert body["details"][0]["allowed"] is True


def test_doctor_dry_run_monkeypatched(client, monkeypatch: pytest.MonkeyPatch) -> None:
    from studio_service.services import mutation

    monkeypatch.setattr(
        mutation,
        "run_doctor_in_workspace",
        lambda _workspace, _repo: (0, "Doctor exited 0", []),
    )
    proposal_id = client.post("/studio/proposals", json=_proposal_payload()).json()["proposal_id"]
    response = client.post(f"/studio/proposals/{proposal_id}/doctor")
    assert response.status_code == 200
    assert response.json()["step"] == "doctor"
    assert response.json()["exit_code"] == 0
