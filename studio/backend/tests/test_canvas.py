from __future__ import annotations


def test_canvas_full_returns_non_empty_graph(client) -> None:
    response = client.get("/studio/canvas/full")
    assert response.status_code == 200
    body = response.json()
    assert len(body["nodes"]) > 0
    assert len(body["edges"]) > 0
    assert body["canvas"]["id"] == "canvas.sdlc_studio.derived_graph"
    assert body["legend"]["categories"]
    assert body["filters"] == {
        "section": None,
        "validation_status": None,
        "entity_type": None,
        "q": None,
    }
    assert body["meta"]["total_nodes"] == len(body["nodes"])
    assert body["meta"]["filtered_nodes"] == len(body["nodes"])


def test_canvas_full_section_filter_reduces_nodes(client) -> None:
    filtered = client.get("/studio/canvas/full", params={"section": "sdlc"}).json()
    assert filtered["filters"]["section"] == "sdlc"
    assert filtered["meta"]["filtered_nodes"] < filtered["meta"]["total_nodes"]
    assert filtered["meta"]["filtered_nodes"] > 0
    assert all(node["category"] == "sdlc" for node in filtered["nodes"])


def test_canvas_full_validation_status_filter_maps_to_overlays(client) -> None:
    response = client.get("/studio/canvas/full", params={"validation_status": "pass"})
    assert response.status_code == 200
    body = response.json()
    assert body["filters"]["validation_status"] == "pass"
    assert all(overlay["status"] == "pass" for overlay in body["overlays"])
    for node in body["nodes"]:
        overlays = node.get("validation_overlays") or []
        if overlays:
            assert all(overlay["status"] == "pass" for overlay in overlays)


def test_canvas_full_entity_type_and_search_filters(client) -> None:
    stages = client.get("/studio/canvas/full", params={"entity_type": "stage"}).json()
    assert stages["meta"]["filtered_nodes"] >= 1
    assert all(node["type"] == "stage" for node in stages["nodes"])

    search = client.get("/studio/canvas/full", params={"q": "implement"}).json()
    assert search["meta"]["filtered_nodes"] >= 1
    assert any("implement" in node["label"].casefold() for node in search["nodes"])


def test_canvas_full_invalid_validation_status(client) -> None:
    response = client.get("/studio/canvas/full", params={"validation_status": "invalid"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CANVAS_FILTER"


def test_canvas_alias_has_etag_and_cache_control(client) -> None:
    response = client.get("/studio/canvas")
    assert response.status_code == 200
    assert response.headers.get("etag")
    assert response.headers.get("cache-control") == "no-store"
    etag = response.headers["etag"]
    not_modified = client.get("/studio/canvas", headers={"If-None-Match": etag})
    assert not_modified.status_code == 304


def test_canvas_node_detail(client) -> None:
    full = client.get("/studio/canvas/full").json()
    display_id = full["nodes"][0]["id"]
    response = client.get(f"/studio/canvas/nodes/{display_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["node"]["id"] == display_id
    assert "source_refs" in body["node"]
    assert "validation_overlays" in body["node"]
    assert isinstance(body["overlays"], list)


def test_canvas_node_not_found(client) -> None:
    response = client.get("/studio/canvas/nodes/display.node.missing")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CANVAS_NODE_NOT_FOUND"


def test_canvas_nodes_include_source_refs_and_legend(client) -> None:
    body = client.get("/studio/canvas/full").json()
    node = body["nodes"][0]
    assert node["source_refs"]
    assert all("ref_type" in ref and "ref" in ref for ref in node["source_refs"])
    assert "validation_statuses" in body["legend"]
