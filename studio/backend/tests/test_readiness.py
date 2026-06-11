from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_readiness_wraps_studio_engine(client) -> None:
    response = client.get("/studio/readiness")
    assert response.status_code == 200
    body = response.json()
    assert "readiness" in body
    assert "summary" in body
    assert "checks" in body
    assert body["readiness"]["id"] == "readiness.sdlc_studio.mvp"


def test_session_gate(client) -> None:
    response = client.get("/studio/session/gate")
    assert response.status_code == 200
    body = response.json()
    assert body["present"] is True
    gate_doc = json.loads((_REPO_ROOT / ".sdlc/memory/session-gate.json").read_text())
    assert body["gate"]["card"] == gate_doc["card"]


def test_session_handoff(client) -> None:
    response = client.get("/studio/session/handoff")
    assert response.status_code == 200
    body = response.json()
    assert body["present"] is True
    next_agent = body["sections"]["Routing"]["Next agent"]
    assert next_agent in (
        "implementer",
        "qa",
        "auto-fixer",
        "reviewer",
        "devops",
    )


def test_dashboard_summary(client) -> None:
    response = client.get("/studio/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert "readiness" in body
    assert "session" in body
    assert "canvas" in body
    assert body["canvas"]["available"] is True
    assert body["canvas"]["nodes"] > 0


def test_engine_compile_validate_canvas(client) -> None:
    compile_resp = client.post("/studio/engine/compile", json={})
    assert compile_resp.status_code == 200
    assert "graph_ir" in compile_resp.json()

    validate_resp = client.post("/studio/engine/validate", json={})
    assert validate_resp.status_code == 200
    assert "summary" in validate_resp.json()

    canvas_resp = client.get("/studio/engine/canvas")
    assert canvas_resp.status_code == 200
    canvas = canvas_resp.json()
    assert "nodes" in canvas
    assert "edges" in canvas
