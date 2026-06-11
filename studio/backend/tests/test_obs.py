from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from studio_service.services.event_bus import reset_event_bus


REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def obs_client(client, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    db_path = tmp_path / "sdlc_obs.db"
    monkeypatch.setenv("STUDIO_OBS_DB_PATH", str(db_path))
    monkeypatch.setenv("SDLC_OBS_DB", str(db_path))
    from studio_service.config import get_settings

    get_settings.cache_clear()
    reset_event_bus()
    yield client
    reset_event_bus()
    get_settings.cache_clear()


def test_timeline_returns_ordered_categories(obs_client) -> None:
    from app.infra.sdlc_obs.store import EventStore
    from studio_service.config import get_settings

    store = EventStore(get_settings().resolved_obs_db_path)
    store.append_event(
        event_type="handoff.updated",
        source="handoff_watcher",
        category="handoff",
        timestamp="2026-06-03T10:00:00Z",
        correlation={"card": "INVES-82"},
        payload={"next_agent": "qa"},
    )
    store.append_event(
        event_type="gateway.shell_denied",
        source="sdlc_pre_gateway",
        category="gateway",
        timestamp="2026-06-03T10:00:01Z",
        correlation={"card": "INVES-82", "run_id": "abc"},
        payload={"command": "bad"},
    )
    reset_event_bus()

    response = obs_client.get("/studio/obs/timeline")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 2
    timestamps = [event["timestamp"] for event in body["events"]]
    assert timestamps == sorted(timestamps)
    categories = {event["category"] for event in body["events"]}
    assert {"handoff", "gateway"}.issubset(categories)
    for event in body["events"]:
        assert event["schema_version"] == "1.0"
    gateway_events = [e for e in body["events"] if e["category"] == "gateway"]
    assert gateway_events
    assert "card:INVES-82" in gateway_events[0]["correlation_id"]


def test_timeline_invalid_category(obs_client) -> None:
    response = obs_client.get("/studio/obs/timeline", params={"category": "invalid"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CATEGORY"


def test_gateway_deny_is_retrievable(obs_client, tmp_path: Path) -> None:
    from studio_service.config import get_settings

    db_path = get_settings().resolved_obs_db_path
    hooks_dir = REPO_ROOT / ".cursor" / "hooks"
    payload = json.dumps({"command": "rm -rf /"})
    env = {**os.environ, "SDLC_OBS_DB": str(db_path)}
    result = subprocess.run(
        [sys.executable, str(hooks_dir / "sdlc_pre_gateway.py")],
        input=payload,
        text=True,
        capture_output=True,
        cwd=str(hooks_dir),
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    body = json.loads(result.stdout)
    assert body["permission"] == "deny"
    reset_event_bus()

    response = obs_client.get(
        "/studio/obs/timeline",
        params={"category": "gateway", "limit": 20},
    )
    assert response.status_code == 200
    events = response.json()["events"]
    denied = [event for event in events if event["event_type"] == "gateway.shell_denied"]
    assert denied, "expected gateway.shell_denied in timeline"
    assert "rm -rf" in denied[-1]["payload"]["command"]


def test_obs_timeline_is_read_only(obs_client) -> None:
    handoff = REPO_ROOT / ".sdlc/memory/orchestrator-handoff.md"
    original = handoff.read_text(encoding="utf-8")
    obs_client.get("/studio/obs/timeline")
    assert handoff.read_text(encoding="utf-8") == original


def test_obs_runs_and_metrics_endpoints(obs_client) -> None:
    runs = obs_client.get("/studio/obs/runs", params={"limit": 5})
    assert runs.status_code == 200
    body = runs.json()
    assert "runs" in body
    assert "count" in body

    metrics = obs_client.get("/studio/obs/metrics")
    assert metrics.status_code == 200
    metrics_body = metrics.json()
    assert "kpis" in metrics_body
    assert "summary" in metrics_body


def test_sse_replay_payload_format() -> None:
    event = {
        "schema_version": "1.0",
        "event_id": "evt_test",
        "event_type": "gateway.shell_denied",
        "category": "gateway",
        "timestamp": "2026-06-03T11:00:00Z",
        "source": "sdlc_pre_gateway",
        "correlation_id": "card:INVES-82",
        "correlation": {"card": "INVES-82"},
        "payload": {"command": "test-sse"},
    }
    payload = json.dumps(event, separators=(",", ":"))
    wire = f"event: studio.obs\ndata: {payload}\n\n"
    assert wire.startswith("event: studio.obs")
    assert "test-sse" in wire
