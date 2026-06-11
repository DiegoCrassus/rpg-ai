from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from studio import CompilerInputError, compile_studio_sources
from studio.engine import compiler_core

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "command_body", "hook_logic", "template_body", "lifecycle_body", "ci_log", "evidence"}


def test_compile_studio_sources_is_deterministic_and_schema_shaped() -> None:
    first = compile_studio_sources(REPO_ROOT)

    assert first == compile_studio_sources(REPO_ROOT)
    _assert_graph_schema_shape(first.graph_ir)
    _assert_workflow_schema_shape(first.workflow_ir)
    assert [node["id"] for node in first.graph_ir["nodes"]] == sorted(node["id"] for node in first.graph_ir["nodes"])
    assert [edge["id"] for edge in first.graph_ir["edges"]] == sorted(edge["id"] for edge in first.graph_ir["edges"])
    assert [item["id"] for item in first.workflow_ir["workflow"]["transitions"]] == sorted(item["id"] for item in first.workflow_ir["workflow"]["transitions"])
    assert [stage["id"] for stage in first.workflow_ir["workflow"]["stages"]] == ["stage.ticket", "stage.requirements", "stage.architecture", "stage.implementation", "stage.validation", "stage.review", "stage.deployment", "stage.observability", "stage.incident", "stage.autofix"]


def test_compile_studio_sources_preserves_source_refs_without_source_bodies() -> None:
    result = compile_studio_sources(REPO_ROOT)

    assert result.graph_ir["graph"]["source_refs"]
    assert all(node["source_refs"] for node in result.graph_ir["nodes"])
    assert all(edge["source_refs"] for edge in result.graph_ir["edges"])
    assert all(stage["source_refs"] for stage in result.workflow_ir["workflow"]["stages"])
    assert all(item["source_refs"] for item in result.workflow_ir["workflow"]["transitions"])
    assert any(node["registry_ref"].startswith("cursor.") and node["source_refs"][0]["ref"].startswith(".cursor/") for node in result.graph_ir["nodes"])
    _assert_standard_report_shape(result.report, kind="compile")
    assert result.report["summary"]["counts"]["graph_nodes"] == len(result.graph_ir["nodes"])
    assert _section_item_values(result.report, "boundaries", "excluded_source_area")
    assert "studio/engine/generated/" in _section_item_values(result.report, "boundaries", "excluded_source_area")
    for payload in (result.graph_ir, result.workflow_ir, result.report):
        _assert_forbidden_body_keys_absent(payload)


def test_compile_studio_sources_reports_missing_required_inputs(tmp_path: Path) -> None:
    with pytest.raises(CompilerInputError, match="Missing required compiler inputs") as exc:
        compile_studio_sources(tmp_path)

    assert ".sdlc/registry/sdlc-artifacts.yaml" in exc.value.missing_paths


def test_compile_studio_sources_reports_unreadable_required_yaml(tmp_path: Path) -> None:
    _write_minimal_required_inputs(tmp_path)
    (tmp_path / ".sdlc/registry/relationships.yaml").write_text("relationships: [\n", encoding="utf-8")

    with pytest.raises(CompilerInputError, match="Unreadable required YAML") as exc:
        compile_studio_sources(tmp_path)

    assert ".sdlc/registry/relationships.yaml" in exc.value.unreadable_yaml


def test_compile_studio_sources_does_not_add_cli_or_persist_outputs() -> None:
    forbidden_paths = [REPO_ROOT / path for path in ("studio/engine/generated", "studio/engine/examples", "specs")]
    before_exists = {path: path.exists() for path in forbidden_paths}
    before_mtime = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in compiler_core.REQUIRED_SOURCE_PATHS}

    compile_studio_sources(REPO_ROOT)

    assert {path: path.exists() for path in forbidden_paths} == before_exists
    assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in compiler_core.REQUIRED_SOURCE_PATHS} == before_mtime
    source = (REPO_ROOT / "studio/engine/compiler_core.py").read_text(encoding="utf-8")
    assert not any(token in source for token in ("argparse", "click", "typer", "__main__", "subprocess", ".write_text("))


def _assert_graph_schema_shape(graph_ir: dict[str, Any]) -> None:
    schema = _load_schema("graph.schema.yaml")
    graph_schema = schema["properties"]["graph"]
    node_schema = schema["properties"]["nodes"]["items"]
    edge_schema = schema["properties"]["edges"]["items"]

    assert set(schema["required"]).issubset(graph_ir)
    assert set(graph_schema["required"]).issubset(graph_ir["graph"])
    assert re.match(graph_schema["properties"]["id"]["pattern"], graph_ir["graph"]["id"])
    _assert_source_ref_objects(graph_ir["graph"]["source_refs"])

    node_types = set(node_schema["properties"]["type"]["enum"])
    categories = set(node_schema["properties"]["category"]["enum"])
    for node in graph_ir["nodes"]:
        assert set(node_schema["required"]).issubset(node)
        assert re.match(node_schema["properties"]["id"]["pattern"], node["id"])
        assert node["type"] in node_types
        assert node["category"] in categories
        _assert_source_ref_objects(node["source_refs"])

    node_ids = {node["id"] for node in graph_ir["nodes"]}
    relations = set(edge_schema["properties"]["relation"]["enum"])
    for edge in graph_ir["edges"]:
        assert set(edge_schema["required"]).issubset(edge)
        assert re.match(edge_schema["properties"]["id"]["pattern"], edge["id"])
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
        assert edge["relation"] in relations
        _assert_source_ref_objects(edge["source_refs"])


def _assert_workflow_schema_shape(workflow_ir: dict[str, Any]) -> None:
    schema = _load_schema("workflow.schema.yaml")
    workflow_schema = schema["properties"]["workflow"]
    stage_schema = workflow_schema["properties"]["stages"]["items"]
    transition_schema = workflow_schema["properties"]["transitions"]["items"]

    assert set(schema["required"]).issubset(workflow_ir)
    workflow = workflow_ir["workflow"]
    assert set(workflow_schema["required"]).issubset(workflow)
    assert all(isinstance(source_ref, str) for source_ref in workflow["source_refs"])
    for stage in workflow["stages"]:
        assert set(stage_schema["required"]).issubset(stage)
        assert all(isinstance(source_ref, str) for source_ref in stage["source_refs"])

    stage_ids = {stage["id"] for stage in workflow["stages"]}
    relations = set(transition_schema["properties"]["relation"]["enum"])
    for transition in workflow["transitions"]:
        assert set(transition_schema["required"]).issubset(transition)
        assert transition["from"] in stage_ids
        assert transition["to"] in stage_ids
        assert transition["relation"] in relations
        assert all(isinstance(source_ref, str) for source_ref in transition["source_refs"])


def _assert_source_ref_objects(source_refs: list[dict[str, Any]]) -> None:
    assert source_refs
    assert all(source_ref["ref_type"] == "path" and source_ref["ref"] for source_ref in source_refs)


def _assert_standard_report_shape(report: dict[str, Any], *, kind: str) -> None:
    assert set(report) == {"id", "kind", "status", "authority", "summary", "sections", "source_refs", "non_goals"}
    assert report["id"] == f"report.studio.{kind}"
    assert report["kind"] == kind
    assert report["status"] in {"pass", "warn", "fail", "not_run"}
    assert report["authority"] == "derived_non_authoritative"
    assert isinstance(report["summary"]["counts"], dict)
    assert report["sections"]
    _assert_source_ref_objects(report["source_refs"])
    assert report["non_goals"]


def _section_item_values(report: dict[str, Any], section_id: str, label: str) -> list[Any]:
    sections = [section for section in report["sections"] if section["id"] == section_id]
    assert len(sections) == 1
    return [item["value"] for item in sections[0]["items"] if item["label"] == label]


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)


def _write_minimal_required_inputs(root: Path) -> None:
    yaml_payloads = {".sdlc/registry/sdlc-artifacts.yaml": {"artifacts": []}, ".sdlc/registry/cursor-artifacts.yaml": {"artifacts": []}, ".sdlc/registry/relationships.yaml": {"relationships": []}, ".sdlc/stages/lifecycle.yaml": {"stages": []}, ".sdlc/workflows/transitions.yaml": {"workflows": []}}
    for source_path in compiler_core.REQUIRED_SOURCE_PATHS:
        path = root / source_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = yaml.safe_dump(yaml_payloads.get(source_path, {}), sort_keys=True) if source_path.endswith((".yaml", ".yml")) else "reference only\n"
        path.write_text(payload, encoding="utf-8")


def _load_schema(name: str) -> dict[str, Any]:
    schema = yaml.safe_load((REPO_ROOT / "studio/engine/schemas" / name).read_text())
    assert isinstance(schema, dict)
    return schema
