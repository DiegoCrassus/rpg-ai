from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from studio import (
    ValidationRunResult,
    build_canvas_from_sources,
    build_canvas_view_model,
    compile_studio_sources,
    validate_compiler_result,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_BODY_KEYS = {
    "body", "content", "prompt", "command_body", "hook_logic", "template_body", "lifecycle_body",
    "ci_log", "evidence", "coordinates", "position", "props", "react_flow_type", "tldraw_shape", "runtime_state",
}
FORBIDDEN_OUTPUT_PATHS = ("studio/engine/generated", "studio/engine/examples", "specs")


def test_canvas_view_model_is_deterministic_and_schema_adjacent() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    validated = validate_compiler_result(compiled, REPO_ROOT)
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_canvas_view_model(compiled, validated).to_dict()

    assert first == build_canvas_view_model(compiled, validated).to_dict()
    assert first == build_canvas_from_sources(REPO_ROOT).to_dict()
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"canvas", "nodes", "edges", "overlays", "sections", "legend"}
    assert first["canvas"]["id"] == "canvas.sdlc_studio.derived_graph"
    assert first["canvas"]["authority"] == "derived_non_authoritative"
    assert first["canvas"]["version"] == "0.1.0"
    assert first["canvas"]["source_refs"]
    assert first["canvas"]["non_goals"]
    assert [node["id"] for node in first["nodes"]] == sorted(node["id"] for node in first["nodes"])
    assert [edge["id"] for edge in first["edges"]] == sorted(edge["id"] for edge in first["edges"])
    assert [overlay["id"] for overlay in first["overlays"]] == sorted(overlay["id"] for overlay in first["overlays"])
    assert [section["id"] for section in first["sections"]] == sorted(section["id"] for section in first["sections"])


def test_canvas_preserves_graph_node_and_edge_refs() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    model = build_canvas_view_model(compiled, validate_compiler_result(compiled, REPO_ROOT)).to_dict()
    graph_node_ids = {node["id"] for node in compiled.graph_ir["nodes"]}
    graph_edge_ids = {edge["id"] for edge in compiled.graph_ir["edges"]}
    display_node_ids = {node["id"] for node in model["nodes"]}

    for node in model["nodes"]:
        assert node["graph_node_id"] in graph_node_ids
        assert node["id"] == f"display.node.{node['graph_node_id'].removeprefix('node.')}"
        assert {"id", "graph_node_id", "label", "type", "category", "source_refs", "annotations", "validation_overlays"} <= set(node)
        _assert_source_refs(node["source_refs"])

    for edge in model["edges"]:
        assert edge["graph_edge_id"] in graph_edge_ids
        assert edge["source"] in display_node_ids
        assert edge["target"] in display_node_ids
        assert {"id", "graph_edge_id", "source", "target", "relation", "source_refs", "validation_overlays"} <= set(edge)
        _assert_source_refs(edge["source_refs"])


def test_validation_overlays_map_to_targets_and_preserve_refs() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    node_id = compiled.graph_ir["nodes"][0]["id"]
    edge_id = compiled.graph_ir["edges"][0]["id"]
    graph_ir = {
        **compiled.graph_ir,
        "nodes": [
            {**compiled.graph_ir["nodes"][0], "validation_attachments": [_validation_record("validation.node.attachment", "node", node_id, "not_run")]},
            *compiled.graph_ir["nodes"][1:],
        ],
    }
    compiled = replace(compiled, graph_ir=graph_ir)
    records = (
        _validation_record("validation.graph.pass", "graph", compiled.graph_ir["graph"]["id"], "pass"),
        _validation_record("validation.node.warn", "node", node_id, "warn"),
        _validation_record("validation.edge.fail", "edge", edge_id, "fail"),
        _validation_record("validation.path.not_run", "path", "studio/engine/canvas_view_model.py", "not_run"),
        _validation_record("validation.workflow.pass", "workflow", compiled.workflow_ir["workflow"]["id"], "pass"),
    )
    validation = ValidationRunResult(
        results=records,
        summary={"pass": 2, "warn": 1, "fail": 1, "not_run": 1},
        report=base_validation.report,
    )

    payload = build_canvas_view_model(compiled, validation).to_dict()
    overlays = {overlay["id"]: overlay for overlay in payload["overlays"]}
    node = _by_graph_id(payload["nodes"], "graph_node_id", node_id)
    edge = _by_graph_id(payload["edges"], "graph_edge_id", edge_id)

    assert set(overlays) == {
        "overlay.validation.edge.fail",
        "overlay.validation.graph.pass",
        "overlay.validation.node.attachment",
        "overlay.validation.node.warn",
        "overlay.validation.path.not_run",
        "overlay.validation.workflow.pass",
    }
    assert {overlay["status"] for overlay in overlays.values()} == {"pass", "warn", "fail", "not_run"}
    assert [overlay["id"] for overlay in node["validation_overlays"]] == ["overlay.validation.node.attachment", "overlay.validation.node.warn"]
    assert [overlay["status"] for overlay in node["validation_overlays"]] == ["not_run", "warn"]
    assert edge["validation_overlays"][0]["id"] == "overlay.validation.edge.fail"
    assert edge["validation_overlays"][0]["status"] == "fail"
    for overlay in overlays.values():
        assert overlay["target"]["ref_type"] in {"graph", "workflow", "node", "edge", "path"}
        _assert_source_refs(overlay["source_refs"])


def test_sections_are_report_summaries_with_source_refs_only() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    payload = build_canvas_view_model(compiled, validate_compiler_result(compiled, REPO_ROOT)).to_dict()
    section_ids = {section["id"] for section in payload["sections"]}

    assert "section.compile.coverage" in section_ids
    assert "section.validate.findings" in section_ids
    for section in payload["sections"]:
        assert {"id", "report_ref", "kind", "title", "status", "summary", "items", "source_refs"} == set(section)
        assert section["kind"] in {"compile", "validate"}
        _assert_source_refs(section["source_refs"])
    _assert_forbidden_body_keys_absent(payload)


def _validation_record(record_id: str, target_type: str, target_ref: str, status: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "target_ref": {"ref_type": target_type, "ref": target_ref},
        "check_type": "custom",
        "status": status,
        "messages": [{"level": "info", "text": f"{status} overlay for {target_type}."}],
        "source_refs": [{"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"}],
    }


def _by_graph_id(records: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    matches = [record for record in records if record[key] == value]
    assert len(matches) == 1
    return matches[0]


def _assert_source_refs(source_refs: list[dict[str, str]]) -> None:
    assert source_refs
    assert all(source_ref["ref_type"] == "path" and source_ref["ref"] for source_ref in source_refs)


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
