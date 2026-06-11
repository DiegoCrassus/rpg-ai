def test_workflow_builder_canvas_has_ten_stages(client) -> None:
    response = client.get("/studio/canvas/workflow-builder")
    assert response.status_code == 200
    body = response.json()
    nodes = body["nodes"]
    assert len(nodes) == 10
    assert all(node["type"] == "stage" for node in nodes)
    labels = {node["label"] for node in nodes}
    assert "Implementation" in labels
    assert "Requirements" in labels


def test_workflow_builder_canvas_includes_transitions(client) -> None:
    body = client.get("/studio/canvas/workflow-builder").json()
    edges = body["edges"]
    assert len(edges) >= 6
    assert all(edge["relation"] == "transitions_to" for edge in edges)
    with_agent = [edge for edge in edges if edge.get("agent")]
    assert len(with_agent) >= 1


def test_metadata_pipeline_lists_agents_and_stages(client) -> None:
    response = client.get("/studio/metadata/pipeline")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["stage_count"] == 10
    assert body["summary"]["agent_count"] >= 6
    assert body["summary"]["gate_count"] >= 1
    assert any(agent["id"] == "implementer" for agent in body["agents"])
    assert any(stage["id"] == "implementation" for stage in body["stages"])
    assert any(gate["stage"] == "implementation" for gate in body["gates"])
