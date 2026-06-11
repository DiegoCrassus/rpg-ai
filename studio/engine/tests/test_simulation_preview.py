from pathlib import Path
from typing import Any

import pytest

from studio.engine.canvas_view_model import build_canvas_view_model
from studio.engine.compiler_core import compile_studio_sources
from studio.engine.simulation_preview import (
    VALID_INTENTS,
    VALID_PATH_LABELS,
    VALID_SCENARIOS,
    VALID_STEP_KINDS,
    VALID_TAGS,
    SimulationPreviewInputError,
    build_simulation_preview_from_sources,
    build_simulation_preview_model,
)
from studio.engine.validation_inspection import build_validation_inspection_model
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "ci_log", "evidence", "coordinates", "props", "runtime_state"}
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")


def test_simulation_preview_is_deterministic_and_schema_shaped() -> None:
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_simulation_preview_from_sources(REPO_ROOT)

    assert first == build_simulation_preview_from_sources(REPO_ROOT)
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"simulation", "summary", "scenarios", "lifecycle_map"}
    assert first["simulation"]["authority"] == "derived_non_authoritative"
    assert first["simulation"]["execution_mode"] == "non_executing_preview"
    assert first["simulation"]["freshness"] == "derived_inputs_only"
    assert first["summary"]["scenario_count"] == len(VALID_SCENARIOS)
    assert first["summary"]["validation_fail"] == 0
    assert set(first["summary"]["path_labels"]) == set(VALID_PATH_LABELS)
    scenario_ids = [item["id"] for item in first["scenarios"]]
    assert scenario_ids == [f"simulation.scenario.{sid}" for sid in VALID_SCENARIOS]
    for scenario in first["scenarios"]:
        assert scenario["id"].removeprefix("simulation.scenario.") in VALID_SCENARIOS
        assert scenario["description"]
        assert scenario["outcome"]
        assert scenario["evidence_expectations"]
        assert all(tag in VALID_TAGS for tag in scenario["tags"])
        for step in scenario["steps"]:
            assert step["path_label"] in VALID_PATH_LABELS
            assert step["kind"] in VALID_STEP_KINDS
            assert step["source_refs"]
            assert step["handoff"]["handoff_ref"] == ".sdlc/memory/orchestrator-handoff.md"
    assert len(first["lifecycle_map"]) == first["summary"]["workflow_transitions"]
    assert all(entry["lifecycle_source"].startswith(".sdlc/") for entry in first["lifecycle_map"])
    _assert_forbidden_body_keys_absent(first)


def test_scenario_filter_and_blocked_path_labels() -> None:
    filtered = build_simulation_preview_from_sources(REPO_ROOT, scenario="qa_failure")
    assert filtered["simulation"]["filters"]["scenario"] == "qa_failure"
    assert len(filtered["scenarios"]) == 1
    labels = {step["path_label"] for step in filtered["scenarios"][0]["steps"]}
    assert "blocked" in labels
    with pytest.raises(SimulationPreviewInputError, match="invalid scenario: bogus"):
        build_simulation_preview_from_sources(REPO_ROOT, scenario="bogus")


def test_intent_path_label_and_step_kind_filters() -> None:
    docs_only = build_simulation_preview_from_sources(REPO_ROOT, intent="DOCS_ONLY")
    assert docs_only["simulation"]["filters"]["intent"] == "DOCS_ONLY"
    assert len(docs_only["scenarios"]) == 1
    assert docs_only["scenarios"][0]["intent"] in VALID_INTENTS

    blocked_steps = build_simulation_preview_from_sources(REPO_ROOT, path_label="blocked")
    assert blocked_steps["simulation"]["filters"]["path_label"] == "blocked"
    assert blocked_steps["summary"]["step_count"] > 0
    assert all(step["path_label"] == "blocked" for scenario in blocked_steps["scenarios"] for step in scenario["steps"])

    transitions = build_simulation_preview_from_sources(REPO_ROOT, step_kind="transition")
    assert transitions["simulation"]["filters"]["step_kind"] == "transition"
    assert all(step["kind"] == "transition" for scenario in transitions["scenarios"] for step in scenario["steps"])

    failure_paths = build_simulation_preview_from_sources(REPO_ROOT, tag="failure_path")
    assert failure_paths["simulation"]["filters"]["tag"] == "failure_path"
    assert {item["id"] for item in failure_paths["scenarios"]} == {
        "simulation.scenario.qa_failure",
        "simulation.scenario.reviewer_escalation",
    }

    with pytest.raises(SimulationPreviewInputError, match="invalid intent: BOGUS"):
        build_simulation_preview_from_sources(REPO_ROOT, intent="BOGUS")
    with pytest.raises(SimulationPreviewInputError, match="invalid path_label: bogus"):
        build_simulation_preview_from_sources(REPO_ROOT, path_label="bogus")
    with pytest.raises(SimulationPreviewInputError, match="invalid step_kind: bogus"):
        build_simulation_preview_from_sources(REPO_ROOT, step_kind="bogus")
    with pytest.raises(SimulationPreviewInputError, match="invalid tag: bogus"):
        build_simulation_preview_from_sources(REPO_ROOT, tag="bogus")


def test_validation_fail_marks_transition_blocked_in_qa_scenario() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    failed = _validation_record("validation.path.fail", "path", "studio/engine/simulation_preview.py", "fail")
    validation = ValidationRunResult(
        results=(*base_validation.results, failed),
        summary={"pass": 6, "warn": 0, "fail": 1, "not_run": 0},
        report=base_validation.report,
    )
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    model = build_simulation_preview_model(compiled, validation, canvas, inspection, scenario="qa_failure")

    blocked_steps = [step for step in model["scenarios"][0]["steps"] if step["path_label"] == "blocked"]
    assert model["summary"]["validation_fail"] == 1
    assert any(step["transition_ref"] == "transition.validation_to_review" for step in blocked_steps)


def _validation_record(record_id: str, target_type: str, target_ref: str, status: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "target_ref": {"ref_type": target_type, "ref": target_ref},
        "check_type": "custom",
        "status": status,
        "messages": [{"level": "error" if status == "fail" else "info", "text": f"{status} simulation record."}],
        "source_refs": [{"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"}],
    }


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
