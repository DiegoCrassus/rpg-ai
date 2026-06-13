from __future__ import annotations

from studio.engine.publish_evidence import EVIDENCE_FIELD_KEYS


def test_evidence_draft_smoke(client) -> None:
    response = client.post("/studio/evidence/draft", json={})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"projection", "summary", "evidence_fields"}
    assert body["projection"]["id"] == "evidence.sdlc_studio.projection"
    assert body["projection"]["execution_mode"] == "non_executing_projection"
    assert set(body["evidence_fields"]) == set(EVIDENCE_FIELD_KEYS)
    assert body["evidence_fields"]["card"] == "RPG-N"


def test_evidence_draft_card_filter(client) -> None:
    response = client.post(
        "/studio/evidence/draft",
        json={
            "card": "RPG-90",
            "title": "[AI][BACKEND] Plane/GitHub integration API",
            "branch": "feature/RPG-90-plane-github-integration-api",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_fields"]["card"] == "RPG-90"
    assert body["evidence_fields"]["artifacts"]["branch"] == (
        "feature/RPG-90-plane-github-integration-api"
    )
    assert body["projection"]["filters"]["card"] == "RPG-90"


def test_evidence_draft_invalid_card(client) -> None:
    response = client.post("/studio/evidence/draft", json={"card": "bogus"})

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "INVALID_EVIDENCE_FILTER"
