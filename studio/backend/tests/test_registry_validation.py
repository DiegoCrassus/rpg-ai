from __future__ import annotations

import pytest


def test_registry_graph_returns_registry_graph_id(client) -> None:
    response = client.get("/studio/registry/graph")
    assert response.status_code == 200
    body = response.json()
    assert body["graph"]["id"] == "graph.sdlc_studio.registry"
    assert len(body["nodes"]) > 0
    assert "broken_refs" in body
    assert "unresolved_relationships" in body["broken_refs"]
    assert "missing_optional_source_paths" in body["broken_refs"]
    assert "summary" in body
    assert "broken_ref_count" in body["summary"]


def test_validation_inspect_default_grouping(client) -> None:
    response = client.get("/studio/validation/inspect")
    assert response.status_code == 200
    body = response.json()
    assert body["inspection"]["id"] == "inspection.sdlc_studio.validation"
    assert body["inspection"]["group_by"] == "status"
    assert "groups" in body
    assert "records" in body
    assert body["summary"]["total_records"] >= body["summary"]["visible_records"]


def test_validation_inspect_status_filter(client) -> None:
    response = client.get("/studio/validation/inspect", params={"status": "pass"})
    assert response.status_code == 200
    body = response.json()
    assert all(record["status"] == "pass" for record in body["records"])


def test_validation_inspect_invalid_filter(client) -> None:
    response = client.get("/studio/validation/inspect", params={"status": "bogus"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_VALIDATION_FILTER"


def test_validation_run_returns_summary(client) -> None:
    response = client.post("/studio/validation/run", json={})
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "results" in body
    assert "report" in body


def test_doctor_run_monkeypatched(client, monkeypatch: pytest.MonkeyPatch) -> None:
    from studio_service.services import foundation_views

    monkeypatch.setattr(
        foundation_views,
        "run_doctor_in_workspace",
        lambda _workspace, _repo: (0, "Doctor exited 0", []),
    )
    response = client.post("/studio/doctor/run", json={})
    assert response.status_code == 200
    assert response.json()["exit_code"] == 0


def test_simulation_preview_smoke(client) -> None:
    response = client.post("/studio/simulation/preview", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["simulation"]["id"] == "simulation.sdlc_studio.preview"
    assert "scenarios" in body


def test_simulation_preview_invalid_scenario(client) -> None:
    response = client.post("/studio/simulation/preview", json={"scenario": "bogus"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SIMULATION_FILTER"


def test_assistance_workflow_smoke(client) -> None:
    response = client.post("/studio/assistance/workflow", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["assistance"]["id"] == "assistance.sdlc_studio.workflow"
    assert "suggestions" in body


def test_assistance_workflow_invalid_kind(client) -> None:
    response = client.post("/studio/assistance/workflow", json={"kind": "bogus"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ASSISTANCE_FILTER"


def test_skeleton_tests_list(client) -> None:
    response = client.get("/studio/skeleton/tests")
    assert response.status_code == 200
    body = response.json()
    assert body["skeleton"]["id"] == "skeleton.sdlc_studio.mvp"
    assert len(body["entries"]) > 0


def test_openapi_registers_s5_routes(client) -> None:
    paths = client.get("/openapi.json").json().get("paths", {})
    assert "/studio/registry/graph" in paths
    assert "/studio/validation/inspect" in paths
    assert "/studio/validation/run" in paths
    assert "/studio/doctor/run" in paths
    assert "/studio/simulation/preview" in paths
    assert "/studio/assistance/workflow" in paths
    assert "/studio/skeleton/tests" in paths
