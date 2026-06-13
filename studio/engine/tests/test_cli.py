from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from studio.engine import compiler_core

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")
REPRESENTATIVE_SOURCE_PATHS = (
    "studio/engine/compiler_core.py",
    "studio/engine/validator_core.py",
    ".sdlc/sdlc.yaml",
)


def test_compile_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("compile")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio compile: derived, non-authoritative output" in completed.stdout
    assert "status: " in completed.stdout
    assert "graph edges: " in completed.stdout
    assert "graph nodes: " in completed.stdout
    assert "required inputs: " in completed.stdout
    assert "workflow stages: " in completed.stdout
    assert "workflow transitions: " in completed.stdout
    assert "unresolved relationships: " in completed.stdout
    assert "derived and non-authoritative only" in completed.stdout


def test_compile_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("compile", "--format", "json")
        second = run_cli("compile", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"graph_ir", "workflow_ir", "report"}
    assert isinstance(payload["graph_ir"], dict)
    assert isinstance(payload["workflow_ir"], dict)
    assert_standard_report_shape(payload["report"], kind="compile")
    assert payload["report"]["summary"]["counts"]["graph_nodes"] == len(payload["graph_ir"]["nodes"])


def test_validate_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("validate")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio validate: derived, non-authoritative output" in completed.stdout
    assert "pass: 6" in completed.stdout
    assert "warn: 0" in completed.stdout
    assert "fail: 0" in completed.stdout
    assert "not run: 0" in completed.stdout
    assert "- validation.graph.relationship_targets: pass" in completed.stdout
    assert "- validation.compiler.authority_boundaries: pass" in completed.stdout


def test_validate_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("validate", "--format", "json")
        second = run_cli("validate", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"report", "results", "summary"}
    assert isinstance(payload["results"], list)
    assert payload["summary"] == {"pass": 6, "warn": 0, "fail": 0, "not_run": 0}
    assert_standard_report_shape(payload["report"], kind="validate")
    assert payload["report"]["summary"]["counts"] == payload["summary"]


def test_canvas_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("canvas")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio canvas: derived, non-authoritative output" in completed.stdout
    assert "authority: derived_non_authoritative" in completed.stdout
    assert "nodes: " in completed.stdout
    assert "edges: " in completed.stdout
    assert "overlays: " in completed.stdout
    assert "transient stdout/in-memory" in completed.stdout


def test_canvas_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("canvas", "--format", "json")
        second = run_cli("canvas", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"canvas", "nodes", "edges", "overlays", "sections", "legend"}
    assert payload["canvas"]["authority"] == "derived_non_authoritative"
    assert payload["canvas"]["id"] == "canvas.sdlc_studio.derived_graph"
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)
    assert isinstance(payload["overlays"], list)
    assert isinstance(payload["sections"], list)


def test_inspect_validation_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("inspect-validation")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio validation inspection: derived, non-authoritative output" in completed.stdout
    assert "authority: derived_non_authoritative" in completed.stdout
    assert "records: 6 visible of 6 total" in completed.stdout
    assert "transient stdout/in-memory" in completed.stdout


def test_inspect_validation_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("inspect-validation", "--format", "json")
        second = run_cli("inspect-validation", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"inspection", "summary", "groups", "records"}
    assert payload["inspection"]["authority"] == "derived_non_authoritative"
    assert payload["inspection"]["canvas_ref"] == "canvas.sdlc_studio.derived_graph"
    assert payload["summary"]["by_status"] == {"pass": 6, "warn": 0, "fail": 0, "not_run": 0}
    assert payload["records"][0]["source_refs"]


def test_inspect_validation_filters_and_grouping_are_deterministic() -> None:
    completed = run_cli(
        "inspect-validation",
        "--format",
        "json",
        "--status",
        "pass",
        "--check-type",
        "policy",
        "--target-type",
        "path",
        "--group-by",
        "target_type",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["inspection"]["filters"] == {"status": "pass", "check_type": "policy", "target_type": "path"}
    assert payload["inspection"]["group_by"] == "target_type"
    assert payload["summary"]["visible_records"] == 2
    assert [group["key"] for group in payload["groups"]] == ["path"]


def test_inspect_validation_invalid_args_exit_nonzero_without_traceback() -> None:
    completed = run_cli("inspect-validation", "--status", "bogus")

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == "error: invalid status: bogus\n"
    assert "Traceback" not in completed.stderr


def test_assist_workflow_cli_smoke_and_kind_filter() -> None:
    with unchanged_repo_outputs():
        text = run_cli("assist-workflow")
        first_json = run_cli("assist-workflow", "--format", "json")
    assert text.returncode == 0 and "derived_non_authoritative" in text.stdout
    assert first_json.returncode == 0 and first_json.stdout == run_cli("assist-workflow", "--format", "json").stdout
    payload = json.loads(first_json.stdout)
    assert set(payload) == {"assistance", "summary", "explanations", "suggestions", "annotations"}
    filtered = json.loads(run_cli("assist-workflow", "--format", "json", "--kind", "workflow_handoff").stdout)
    assert filtered["assistance"]["filters"] == {"kind": "workflow_handoff"}


def test_preview_simulation_cli_smoke_and_scenario_filter() -> None:
    with unchanged_repo_outputs():
        text = run_cli("preview-simulation")
        first_json = run_cli("preview-simulation", "--format", "json")
    assert text.returncode == 1 and "non_executing_preview" in text.stdout
    assert "execution_mode: non_executing_preview" in text.stdout
    assert "outcome=" in text.stdout
    assert first_json.returncode == 1 and first_json.stdout == run_cli("preview-simulation", "--format", "json").stdout
    payload = json.loads(first_json.stdout)
    assert set(payload) == {"simulation", "summary", "scenarios", "lifecycle_map"}
    assert set(payload["simulation"]["filters"]) == {"scenario", "intent", "path_label", "step_kind", "tag"}
    filtered = json.loads(run_cli("preview-simulation", "--format", "json", "--scenario", "devops_finish").stdout)
    assert filtered["simulation"]["filters"]["scenario"] == "devops_finish"
    assert len(filtered["scenarios"]) == 1
    tag_filtered = json.loads(run_cli("preview-simulation", "--format", "json", "--tag", "docs_scope").stdout)
    assert tag_filtered["simulation"]["filters"]["tag"] == "docs_scope"
    assert len(tag_filtered["scenarios"]) == 1
    bogus = run_cli("preview-simulation", "--scenario", "bogus")
    assert bogus.returncode == 1 and bogus.stderr == "error: invalid scenario: bogus\n"


def test_check_readiness_cli_smoke_and_deterministic_json() -> None:
    with unchanged_repo_outputs():
        text = run_cli("check-readiness")
        first_json = run_cli("check-readiness", "--format", "json")
    assert text.returncode == 0 and "non_executing_readiness_loop" in text.stdout
    assert "mvp_ready: True" in text.stdout
    assert "check-readiness" in text.stdout
    assert first_json.returncode == 0 and first_json.stdout == run_cli("check-readiness", "--format", "json").stdout
    payload = json.loads(first_json.stdout)
    assert set(payload) == {"readiness", "summary", "checks", "cli_commands"}
    assert payload["readiness"]["authority"] == "derived_non_authoritative"
    assert payload["summary"]["mvp_ready"] is True
    assert payload["summary"]["fail"] == 0


def test_list_skeleton_cli_smoke_and_deterministic_json() -> None:
    with unchanged_repo_outputs():
        text = run_cli("list-skeleton")
        first_json = run_cli("list-skeleton", "--format", "json")
    assert text.returncode == 0 and "non_executing_traceability_plan" in text.stdout
    assert "execution_claimed: False" in text.stdout
    assert "RPG-53" in text.stdout
    assert first_json.returncode == 0 and first_json.stdout == run_cli("list-skeleton", "--format", "json").stdout
    payload = json.loads(first_json.stdout)
    assert set(payload) == {"skeleton", "summary", "entries", "validation_types"}
    assert payload["skeleton"]["card"] == "RPG-75"
    assert payload["summary"]["execution_claimed"] is False
    assert payload["summary"]["phase_count"] == 10


def test_publish_evidence_cli_smoke_and_card_filter() -> None:
    with unchanged_repo_outputs():
        text = run_cli("publish-evidence")
        first_json = run_cli("publish-evidence", "--format", "json")
    assert text.returncode == 0 and "derived_non_authoritative" in text.stdout
    assert "non_executing_projection" in text.stdout
    assert "transient stdout/in-memory" in text.stdout
    assert first_json.returncode == 0 and first_json.stdout == run_cli("publish-evidence", "--format", "json").stdout
    payload = json.loads(first_json.stdout)
    assert set(payload) == {"projection", "summary", "evidence_fields"}
    assert set(payload["evidence_fields"]) == {
        "card",
        "title",
        "summary",
        "problems_solved",
        "technical",
        "validation",
        "artifacts",
        "context_for_future",
    }
    filtered = json.loads(
        run_cli(
            "publish-evidence",
            "--format",
            "json",
            "--card",
            "RPG-72",
            "--branch",
            "feature/RPG-72-publish-evidence-workflow",
        ).stdout
    )
    assert filtered["projection"]["filters"]["card"] == "RPG-72"
    assert filtered["evidence_fields"]["artifacts"]["branch"] == "feature/RPG-72-publish-evidence-workflow"
    bogus = run_cli("publish-evidence", "--card", "bogus")
    assert bogus.returncode == 1 and bogus.stderr == "error: invalid card: bogus\n"


def test_assist_workflow_invalid_kind_exits_nonzero_without_traceback() -> None:
    completed = run_cli("assist-workflow", "--kind", "bogus")

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == "error: invalid kind: bogus\n"
    assert "Traceback" not in completed.stderr


def test_assist_workflow_exits_nonzero_when_validation_failures_present(tmp_path: Path) -> None:
    root = copy_required_inputs(tmp_path)
    artifact_path = root / ".sdlc/registry/sdlc-artifacts.yaml"
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["artifacts"][0]["path"] = "app/forbidden.py"
    artifact_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    completed = run_cli("assist-workflow", "--format", "json", "--root", str(root))

    assert completed.returncode == 1
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["summary"]["validation_fail"] > 0
    assert not (root / "studio/engine/generated").exists()


def test_inspect_validation_exits_nonzero_when_visible_records_fail(tmp_path: Path) -> None:
    root = copy_required_inputs(tmp_path)
    artifact_path = root / ".sdlc/registry/sdlc-artifacts.yaml"
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["artifacts"][0]["path"] = "app/forbidden.py"
    artifact_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    completed = run_cli("inspect-validation", "--format", "json", "--status", "fail", "--root", str(root))

    assert completed.returncode == 1
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["summary"]["by_status"]["fail"] > 0
    assert all(record["status"] == "fail" for record in payload["records"])
    assert not (root / "studio/engine/generated").exists()


def test_compile_bad_root_exits_nonzero_with_concise_stderr(tmp_path: Path) -> None:
    completed = run_cli("compile", "--root", str(tmp_path / "missing"))

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "Missing required compiler inputs" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_validate_bad_root_exits_nonzero_with_concise_stderr(tmp_path: Path) -> None:
    completed = run_cli("validate", "--root", str(tmp_path / "missing"))

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "Missing required compiler inputs" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_output_does_not_include_source_bodies_or_persisted_evidence() -> None:
    completed = run_cli("canvas", "--format", "json")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert_forbidden_keys_absent(payload)


def test_cli_preserves_all_required_source_mtimes() -> None:
    before = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in compiler_core.REQUIRED_SOURCE_PATHS}

    completed = run_cli("compile")

    assert completed.returncode == 0
    assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in before} == before


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "studio.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_required_inputs(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative_path in compiler_core.REQUIRED_SOURCE_PATHS:
        source = REPO_ROOT / relative_path
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return root


class unchanged_repo_outputs:
    def __enter__(self) -> None:
        self._forbidden_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
        self._source_mtimes = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in REPRESENTATIVE_SOURCE_PATHS}

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == self._forbidden_exists
        assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in REPRESENTATIVE_SOURCE_PATHS} == self._source_mtimes


def assert_forbidden_keys_absent(value: object) -> None:
    forbidden = {
        "body",
        "content",
        "prompt",
        "command_body",
        "hook_logic",
        "template_body",
        "lifecycle_body",
        "ci_log",
        "evidence",
    }
    if isinstance(value, dict):
        assert not (set(value) & forbidden)
        for child in value.values():
            assert_forbidden_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            assert_forbidden_keys_absent(child)


def assert_standard_report_shape(report: object, *, kind: str) -> None:
    assert isinstance(report, dict)
    assert set(report) == {"id", "kind", "status", "authority", "summary", "sections", "source_refs", "non_goals"}
    assert report["id"] == f"report.studio.{kind}"
    assert report["kind"] == kind
    assert report["authority"] == "derived_non_authoritative"
    assert isinstance(report["summary"], dict)
    assert isinstance(report["summary"]["counts"], dict)
    assert report["sections"]
    assert report["source_refs"]
    assert report["non_goals"]
