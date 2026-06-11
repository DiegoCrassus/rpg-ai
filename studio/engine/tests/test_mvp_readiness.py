from __future__ import annotations

from pathlib import Path

from studio.engine.canvas_view_model import build_canvas_view_model
from studio.engine.compiler_core import compile_studio_sources
from studio.engine.mvp_readiness import CLI_COMMANDS, build_mvp_readiness_from_sources
from studio.engine.validation_inspection import build_validation_inspection_model
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "ci_log", "coordinates", "props", "runtime_state"}
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")


def test_mvp_readiness_is_deterministic_and_checklist_shaped() -> None:
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_mvp_readiness_from_sources(REPO_ROOT)

    assert first == build_mvp_readiness_from_sources(REPO_ROOT)
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"readiness", "summary", "checks", "cli_commands"}
    assert first["readiness"]["execution_mode"] == "non_executing_readiness_loop"
    assert first["summary"]["fail"] == 0 and first["summary"]["mvp_ready"] is True
    assert [check["id"] for check in first["checks"]] == [
        "readiness.compiler",
        "readiness.validator",
        "readiness.canvas",
        "readiness.inspection",
        "readiness.assistance",
        "readiness.simulation",
        "readiness.publish_evidence",
        "readiness.operating_model",
    ]
    assert first["cli_commands"] == list(CLI_COMMANDS)
    _assert_forbidden_body_keys_absent(first)


def test_readiness_fails_when_validation_failures_present() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    failed = {
        "id": "validation.path.fail",
        "status": "fail",
        "check_type": "policy",
        "target_type": "path",
        "target_ref": "studio/engine/mvp_readiness.py",
        "message": "test failure",
        "next_action": "fix test fixture",
        "source_refs": [{"ref_type": "path", "ref": "studio/engine/mvp_readiness.py"}],
    }
    validation = ValidationRunResult(
        results=(*base_validation.results, failed),
        summary={"pass": 6, "warn": 0, "fail": 1, "not_run": 0},
        report=base_validation.report,
    )
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    from studio.engine.mvp_readiness import MODULE_CHECKS, _module_check
    from studio.engine.publish_evidence import build_publish_evidence_model
    from studio.engine.simulation_preview import build_simulation_preview_model
    from studio.engine.workflow_assistance import build_workflow_assistance_model

    derived = {
        "readiness.assistance": build_workflow_assistance_model(compiled, validation, canvas, inspection),
        "readiness.simulation": build_simulation_preview_model(compiled, validation, canvas, inspection),
        "readiness.publish_evidence": build_publish_evidence_model(compiled, validation, canvas, inspection),
    }
    checks = [
        _module_check(REPO_ROOT, spec, derived.get(spec[0], {}), 1, canvas)
        for spec in MODULE_CHECKS
        if spec[0] in derived
    ]
    assert any(check["status"] == "fail" for check in checks)


def _assert_forbidden_body_keys_absent(value: object) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
