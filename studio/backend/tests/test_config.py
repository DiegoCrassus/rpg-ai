from __future__ import annotations


def test_list_agent_files(client) -> None:
    response = client.get("/studio/config/files", params={"kind": "agent"})
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "agent"
    paths = [entry["path"] for entry in body["files"]]
    assert any(p.endswith(".cursor/agents/implementer.md") for p in paths)


def test_list_with_query_filters(client) -> None:
    response = client.get("/studio/config/files", params={"kind": "agent", "q": "qa"})
    assert response.status_code == 200
    paths = [entry["path"] for entry in response.json()["files"]]
    assert all("qa" in path.lower() for path in paths)


def test_read_existing_file(client) -> None:
    response = client.get(
        "/studio/config/file",
        params={"path": ".cursor/agents/implementer.md"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["exists"] is True
    assert "# Subagent: Implementer" in body["content"]


def test_read_rejects_forbidden_path(client) -> None:
    response = client.get(
        "/studio/config/file",
        params={"path": ".sdlc/memory/orchestrator-handoff.md"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "path_not_allowed"
