from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from studio.engine.canvas_view_model import build_canvas_view_model
from studio.engine.compiler_core import compile_studio_sources
from studio.engine.publish_evidence import (
    EVIDENCE_FIELD_KEYS,
    PublishEvidenceInputError,
    build_publish_evidence_from_sources,
    build_publish_evidence_model,
)
from studio.engine.validation_inspection import build_validation_inspection_model
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "ci_log", "coordinates", "props", "runtime_state"}
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")


def test_publish_evidence_is_deterministic_and_template_shaped() -> None:
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_publish_evidence_from_sources(REPO_ROOT)

    assert first == build_publish_evidence_from_sources(REPO_ROOT)
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"projection", "summary", "evidence_fields"}
    assert first["projection"]["authority"] == "derived_non_authoritative"
    assert first["projection"]["execution_mode"] == "non_executing_projection"
    assert first["projection"]["template_ref"] == ".sdlc/templates/plane/evidence-template.json"
    assert set(first["evidence_fields"]) == set(EVIDENCE_FIELD_KEYS)
    assert first["summary"]["validation_fail"] == 0
    assert first["evidence_fields"]["card"] == "INVES-N"
    assert first["evidence_fields"]["technical"]["modules"]
    assert first["evidence_fields"]["validation"]["doctor"].startswith("not run from Studio")
    assert first["projection"]["source_refs"]
    _assert_forbidden_body_keys_absent(first)


def test_card_title_branch_filters_and_failure_projection() -> None:
    filtered = build_publish_evidence_from_sources(
        REPO_ROOT,
        card="INVES-72",
        title="[AI][SDLC] Publish evidence workflow",
        branch="feature/INVES-72-publish-evidence-workflow",
    )
    assert filtered["projection"]["filters"] == {
        "card": "INVES-72",
        "title": "[AI][SDLC] Publish evidence workflow",
        "branch": "feature/INVES-72-publish-evidence-workflow",
    }
    assert filtered["evidence_fields"]["card"] == "INVES-72"
    assert filtered["evidence_fields"]["artifacts"]["branch"] == "feature/INVES-72-publish-evidence-workflow"

    with pytest.raises(PublishEvidenceInputError, match="invalid card: bogus"):
        build_publish_evidence_from_sources(REPO_ROOT, card="bogus")

    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    failed = _validation_record("validation.path.fail", "path", "studio/engine/publish_evidence.py", "fail")
    validation = ValidationRunResult(
        results=(*base_validation.results, failed),
        summary={"pass": 6, "warn": 0, "fail": 1, "not_run": 0},
        report=base_validation.report,
    )
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    model = build_publish_evidence_model(compiled, validation, canvas, inspection, card="INVES-72")

    assert model["summary"]["validation_fail"] == 1
    assert any("fail validation" in item for item in model["evidence_fields"]["problems_solved"])
    assert "Resolve derived validation failures" in model["evidence_fields"]["context_for_future"][0]


def _validation_record(record_id: str, target_type: str, target_ref: str, status: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "target_ref": {"ref_type": target_type, "ref": target_ref},
        "check_type": "custom",
        "status": status,
        "messages": [{"level": "error" if status == "fail" else "info", "text": f"{status} publish evidence record."}],
        "source_refs": [{"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"}],
    }


def _assert_forbidden_body_keys_absent(value: object) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
