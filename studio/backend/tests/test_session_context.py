from __future__ import annotations

from pathlib import Path

from studio_service.services.session_context import enrich_session


def test_enrich_session_uses_open_gate() -> None:
    session = enrich_session(
        repo_root=__import__("pathlib").Path("."),
        gate={
            "gate_status": "open",
            "card": "INVES-1",
            "branch": "feature/INVES-1-x",
            "stage": "implementation",
        },
        handoff_sections={"Routing": {"Next agent": "implementer", "Stage complete": "no"}},
    )
    assert session["gate_open"] is True
    assert session["execution_active"] is True
    assert session["live_source"] == "gate"
    assert session["stage"] == "implementation"


def test_enrich_session_derives_from_handoff_when_gate_closed(tmp_path: Path) -> None:
    session = enrich_session(
        repo_root=tmp_path,
        gate={"gate_status": "closed", "card": "", "branch": "", "stage": ""},
        handoff_sections={
            "Routing": {"Next agent": "planner", "Stage complete": "yes"},
            "Session": {"Card": "—", "Branch": "—", "Stage": "—"},
        },
        recent_events=[],
    )
    assert session["gate_open"] is False
    assert session["execution_active"] is True
    assert session["live_source"] == "handoff"
    assert session["stage"] == "ticket"
    assert session["inferred_stage"] is True


def test_enrich_session_advances_stage_when_handoff_stage_complete(tmp_path: Path) -> None:
    session = enrich_session(
        repo_root=tmp_path,
        gate={"gate_status": "closed"},
        handoff_sections={
            "Routing": {"Next agent": "implementer", "Stage complete": "yes"},
            "Session": {"Card": "INVES-116", "Branch": "feature/INVES-117-x", "Stage": "architecture"},
        },
        recent_events=[],
    )
    assert session["execution_active"] is True
    assert session["stage"] == "implementation"
    assert session["inferred_stage"] is True


def test_enrich_session_uses_observability_correlation(tmp_path: Path) -> None:
    session = enrich_session(
        repo_root=tmp_path,
        gate={"gate_status": "closed"},
        handoff_sections={"Routing": {"Next agent": "qa", "Stage complete": "no"}},
        recent_events=[
            {
                "timestamp": "2099-06-03T12:00:00Z",
                "correlation": {
                    "card": "INVES-83",
                    "branch": "feature/INVES-83-studio",
                },
            }
        ],
    )
    assert session["execution_active"] is True
    assert session["card"] == "INVES-83"
    assert session["branch"] == "feature/INVES-83-studio"
    assert session["stage"] == "validation"
    assert session["live_source"] == "observability"
