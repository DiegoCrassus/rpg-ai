from __future__ import annotations

from pathlib import Path


def test_health_liveness(client) -> None:
    response = client.get("/studio/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["repo_root_reachable"] is True
    assert "version" in body
    assert body["repo_root"].endswith("sdlc-ai") or "sdlc" in body["repo_root"]


def test_health_no_marketpulse_import() -> None:
    root = Path(__file__).resolve().parents[1] / "src/studio_service"
    for path in root.rglob("*.py"):
        assert "marketpulse" not in path.read_text(encoding="utf-8")
