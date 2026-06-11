from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from studio import (
    ValidationRunResult,
    compile_studio_sources,
    validate_compiler_result,
    validate_studio_sources,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_CLI_TOKENS = ("argparse", "click", "typer", "__main__", "subprocess", ".write_text(")


def test_validate_studio_sources_is_deterministic_and_schema_shaped() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    first = validate_compiler_result(compiled, REPO_ROOT)

    assert isinstance(first, ValidationRunResult)
    assert first == validate_compiler_result(compiled, REPO_ROOT)
    assert first == validate_studio_sources(REPO_ROOT)
    assert first.summary == {"pass": 6, "warn": 0, "fail": 0, "not_run": 0}
    assert [record["id"] for record in first.results] == [
        "validation.graph.relationship_targets",
        "validation.workflow.transition_targets",
        "validation.graph.source_refs",
        "validation.workflow.source_refs",
        "validation.compiler.output_boundaries",
        "validation.compiler.authority_boundaries",
    ]
    _assert_standard_report_shape(first.report, kind="validate")
    assert first.report["summary"]["counts"] == first.summary
    assert _section_item_statuses(first.report, "findings") == {record["id"]: record["status"] for record in first.results}
    for record in first.results:
        _assert_validation_result_shape(record)


def test_broken_graph_edge_target_fails() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    graph_ir = deepcopy(compiled.graph_ir)
    graph_ir["edges"][0]["to"] = "node.missing_target"
    broken = type(compiled)(graph_ir=graph_ir, workflow_ir=compiled.workflow_ir, report=compiled.report)

    record = _record(validate_compiler_result(broken, REPO_ROOT), "validation.graph.relationship_targets")

    assert record["status"] == "fail"
    assert any(message["level"] == "error" and "missing node" in message["text"] for message in record["messages"])
    assert record["source_refs"]
    _assert_validation_result_shape(record)


def test_broken_workflow_transition_target_fails() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    workflow_ir = deepcopy(compiled.workflow_ir)
    workflow_ir["workflow"]["transitions"][0]["from"] = "stage.missing_source"
    broken = type(compiled)(graph_ir=compiled.graph_ir, workflow_ir=workflow_ir, report=compiled.report)

    record = _record(validate_compiler_result(broken, REPO_ROOT), "validation.workflow.transition_targets")

    assert record["status"] == "fail"
    assert any(message["level"] == "error" and "missing stage" in message["text"] for message in record["messages"])
    assert record["source_refs"]
    _assert_validation_result_shape(record)


def test_source_ref_path_existence_and_scope_behavior() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    graph_ir = deepcopy(compiled.graph_ir)
    workflow_ir = deepcopy(compiled.workflow_ir)
    graph_ir["nodes"][0]["source_refs"] = [{"ref_type": "path", "ref": "app/forbidden.py"}]
    workflow_ir["workflow"]["stages"][0]["source_refs"] = ["docs/missing-validator-source.md"]
    broken = type(compiled)(graph_ir=graph_ir, workflow_ir=workflow_ir, report=compiled.report)
    validated = validate_compiler_result(broken, REPO_ROOT)

    graph_record = _record(validated, "validation.graph.source_refs")
    workflow_record = _record(validated, "validation.workflow.source_refs")

    assert graph_record["status"] == "fail"
    assert any(message.get("path") == "app/forbidden.py" for message in graph_record["messages"])
    assert workflow_record["status"] == "fail"
    assert any(message.get("path") == "docs/missing-validator-source.md" for message in workflow_record["messages"])
    _assert_validation_result_shape(graph_record)
    _assert_validation_result_shape(workflow_record)


def test_source_ref_traversal_resolving_into_forbidden_root_fails() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    graph_ir = deepcopy(compiled.graph_ir)
    traversal_ref = "studio/../app/frontend/package.json"
    graph_ir["nodes"][0]["source_refs"] = [traversal_ref]
    broken = type(compiled)(graph_ir=graph_ir, workflow_ir=compiled.workflow_ir, report=compiled.report)

    record = _record(validate_compiler_result(broken, REPO_ROOT), "validation.graph.source_refs")

    assert record["status"] == "fail"
    expected_text = f"Source ref is outside allowed scopes: {traversal_ref}."
    assert record["messages"] == [{"level": "error", "text": expected_text, "path": traversal_ref}]
    _assert_validation_result_shape(record)


def test_validate_studio_sources_does_not_add_cli_or_persist_outputs() -> None:
    forbidden_paths = [REPO_ROOT / path for path in ("studio/engine/generated", "studio/engine/examples", "specs")]
    before_exists = {path: path.exists() for path in forbidden_paths}
    before_mtime = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in ("studio/engine/validator_core.py", "studio/engine/compiler_core.py")}

    validate_studio_sources(REPO_ROOT)

    assert {path: path.exists() for path in forbidden_paths} == before_exists
    assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in before_mtime} == before_mtime
    source = (REPO_ROOT / "studio/engine/validator_core.py").read_text(encoding="utf-8")
    assert not any(token in source for token in FORBIDDEN_CLI_TOKENS)


def _record(result: ValidationRunResult, result_id: str) -> dict[str, Any]:
    matches = [record for record in result.results if record["id"] == result_id]
    assert len(matches) == 1
    return matches[0]


def _assert_validation_result_shape(record: dict[str, Any]) -> None:
    schema = _load_schema("validation-result.schema.yaml")
    target_schema = schema["definitions"]["target_ref"]
    source_schema = schema["definitions"]["source_ref"]
    message_schema = schema["definitions"]["message"]

    assert set(schema["required"]).issubset(record)
    assert re.match(schema["properties"]["id"]["pattern"], record["id"])
    assert record["check_type"] in set(schema["properties"]["check_type"]["enum"])
    assert record["status"] in set(schema["properties"]["status"]["enum"])
    assert "checked_at" not in record
    assert set(target_schema["required"]).issubset(record["target_ref"])
    assert record["target_ref"]["ref_type"] in set(target_schema["properties"]["ref_type"]["enum"])
    assert record["target_ref"]["ref"]

    assert record["messages"]
    for message in record["messages"]:
        assert set(message_schema["required"]).issubset(message)
        assert message["level"] in set(message_schema["properties"]["level"]["enum"])
        assert 0 < len(message["text"]) <= message_schema["properties"]["text"]["maxLength"]

    assert record["source_refs"]
    assert len(record["source_refs"]) == len({(item["ref_type"], item["ref"]) for item in record["source_refs"]})
    for source_ref in record["source_refs"]:
        assert set(source_schema["required"]).issubset(source_ref)
        assert source_ref["ref_type"] in set(source_schema["properties"]["ref_type"]["enum"])
        assert source_ref["ref"]


def _assert_standard_report_shape(report: dict[str, Any], *, kind: str) -> None:
    assert set(report) == {"id", "kind", "status", "authority", "summary", "sections", "source_refs", "non_goals"}
    assert report["id"] == f"report.studio.{kind}"
    assert report["kind"] == kind
    assert report["status"] in {"pass", "warn", "fail", "not_run"}
    assert report["authority"] == "derived_non_authoritative"
    assert isinstance(report["summary"]["counts"], dict)
    assert report["sections"]
    assert report["source_refs"]
    assert report["non_goals"]


def _section_item_statuses(report: dict[str, Any], section_id: str) -> dict[str, str]:
    sections = [section for section in report["sections"] if section["id"] == section_id]
    assert len(sections) == 1
    return {item["label"]: item["status"] for item in sections[0]["items"]}


def _load_schema(name: str) -> dict[str, Any]:
    schema = yaml.safe_load((REPO_ROOT / "studio/engine/schemas" / name).read_text())
    assert isinstance(schema, dict)
    return schema
