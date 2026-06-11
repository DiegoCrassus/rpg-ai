from pathlib import Path
from typing import Any

import pytest

from studio.engine.canvas_view_model import build_canvas_view_model
from studio.engine.compiler_core import compile_studio_sources
from studio.engine.validation_inspection import build_validation_inspection_model
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result
from studio.engine.workflow_assistance import (
    VALID_SUGGESTION_KINDS,
    WorkflowAssistanceInputError,
    build_workflow_assistance_from_sources,
    build_workflow_assistance_model,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "ci_log", "evidence", "coordinates", "props", "runtime_state"}
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")


def test_workflow_assistance_is_deterministic_and_schema_shaped() -> None:
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_workflow_assistance_from_sources(REPO_ROOT)

    assert first == build_workflow_assistance_from_sources(REPO_ROOT)
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"assistance", "summary", "explanations", "suggestions", "annotations"}
    assert first["assistance"]["authority"] == "derived_non_authoritative"
    assert first["assistance"]["freshness"] == "derived_inputs_only"
    assert first["summary"]["validation_fail"] == 0
    assert first["summary"]["explanation_count"] == 3
    assert _ids(first["explanations"]) == sorted(_ids(first["explanations"]))
    assert _ids(first["suggestions"]) == sorted(_ids(first["suggestions"]))
    for record in (*first["explanations"], *first["suggestions"], *first["annotations"]):
        assert record["source_refs"]
    for suggestion in first["suggestions"]:
        assert suggestion["kind"] in VALID_SUGGESTION_KINDS and suggestion["status"] == "advisory"
    _assert_forbidden_body_keys_absent(first)


def test_kind_filter_and_failure_heuristics() -> None:
    filtered = build_workflow_assistance_from_sources(REPO_ROOT, kind="workflow_handoff")
    assert filtered["assistance"]["filters"] == {"kind": "workflow_handoff"}
    assert all(item["kind"] == "workflow_handoff" for item in filtered["suggestions"])
    with pytest.raises(WorkflowAssistanceInputError, match="invalid kind: bogus"):
        build_workflow_assistance_from_sources(REPO_ROOT, kind="bogus")

    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    failed = _validation_record("validation.path.fail", "path", "studio/engine/workflow_assistance.py", "fail")
    validation = ValidationRunResult(
        results=(*base_validation.results, failed),
        summary={"pass": 6, "warn": 0, "fail": 1, "not_run": 0},
        report=base_validation.report,
    )
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    model = build_workflow_assistance_model(compiled, validation, canvas, inspection)

    kinds = {item["kind"] for item in model["suggestions"]}
    assert model["summary"]["validation_fail"] == 1
    assert {"validation_gap", "risk_summary", "plane_follow_up_draft"} <= kinds
    draft = next(item for item in model["suggestions"] if item["kind"] == "plane_follow_up_draft")
    assert "do not apply from Studio output" in draft["plane_follow_up_draft"]["reminder"]


def _validation_record(record_id: str, target_type: str, target_ref: str, status: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "target_ref": {"ref_type": target_type, "ref": target_ref},
        "check_type": "custom",
        "status": status,
        "messages": [{"level": "error" if status == "fail" else "info", "text": f"{status} assistance record."}],
        "source_refs": [{"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"}],
    }


def _ids(records: list[dict[str, Any]]) -> list[str]:
    return [record["id"] for record in records]


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
