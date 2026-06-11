"""Derived, non-authoritative Studio canvas view model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from studio.engine.compiler_core import CompilerResult, compile_studio_sources
from studio.engine.reporting import AUTHORITY, STATUSES
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

CANVAS_ID = "canvas.sdlc_studio.derived_graph"
CANVAS_VERSION = "0.1.0"
CANVAS_SOURCE_REFS = (
    {"ref_type": "path", "ref": "studio/engine/canvas_view_model.py"},
    {"ref_type": "path", "ref": "studio/docs/contracts/visual-orchestration-prototype.md"},
    {"ref_type": "path", "ref": "studio/docs/contracts/graph-ir-contract.md"},
    {"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"},
)
CANVAS_NON_GOALS = (
    "Does not replace Graph IR, Workflow IR, .sdlc/, .cursor/, Plane, GitHub, or registry authority.",
    "Does not persist canvas outputs, generated artifacts, screenshots, reports, local tickets, or evidence.",
    "Does not define UI components, canvas coordinates, React Flow nodes, TLDraw shapes, APIs, or runtime state.",
)


@dataclass(frozen=True)
class CanvasViewModel:
    canvas: dict[str, Any]
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    overlays: tuple[dict[str, Any], ...]
    sections: tuple[dict[str, Any], ...]
    legend: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "canvas": self.canvas,
            "nodes": list(self.nodes),
            "edges": list(self.edges),
            "overlays": list(self.overlays),
            "sections": list(self.sections),
            "legend": self.legend,
        }


def build_canvas_from_sources(root: Any) -> CanvasViewModel:
    """Compile, validate, and derive the canvas view model in memory."""

    compiled = compile_studio_sources(root)
    validation = validate_compiler_result(compiled, root)
    return build_canvas_view_model(compiled, validation)


def build_canvas_view_model(compiled: CompilerResult, validation: ValidationRunResult) -> CanvasViewModel:
    """Build deterministic renderer-friendly records from compiler and validator IR."""

    graph = _dict(compiled.graph_ir.get("graph"))
    graph_id = str(graph.get("id", "graph.unknown"))
    workflow = _dict(compiled.workflow_ir.get("workflow"))
    overlays = _validation_overlays(compiled, validation)
    overlays_by_target = _overlays_by_target(overlays)

    nodes = tuple(_display_node(node, overlays_by_target) for node in _sorted_dicts(compiled.graph_ir.get("nodes")))
    edges = tuple(_display_edge(edge, overlays_by_target) for edge in _sorted_dicts(compiled.graph_ir.get("edges")))
    sections = tuple(_report_sections(compiled.report, "compile")) + tuple(_report_sections(validation.report, "validate"))
    canvas = {
        "id": CANVAS_ID,
        "name": "SDLC Studio Derived Graph Canvas",
        "version": CANVAS_VERSION,
        "authority": AUTHORITY,
        "source_refs": _unique_source_refs([*CANVAS_SOURCE_REFS, *_source_refs(graph.get("source_refs"))]),
        "graph_ref": graph_id,
        "workflow_ref": str(workflow.get("id", "workflow.unknown")),
        "non_goals": list(CANVAS_NON_GOALS),
        "validation_overlays": _summaries(_target_matches(overlays_by_target, "canvas", CANVAS_ID)),
    }
    return CanvasViewModel(
        canvas=canvas,
        nodes=nodes,
        edges=edges,
        overlays=tuple(overlays),
        sections=sections,
        legend=_legend(nodes, overlays),
    )


def render_canvas_text(model: CanvasViewModel) -> str:
    """Render a concise stdout-only summary of the derived canvas."""

    payload = model.to_dict()
    counts = {"nodes": len(payload["nodes"]), "edges": len(payload["edges"]), "overlays": len(payload["overlays"]), "sections": len(payload["sections"])}
    lines = [
        "Studio canvas: derived, non-authoritative output",
        f"canvas: {payload['canvas']['id']}",
        f"authority: {payload['canvas']['authority']}",
        *(f"{key}: {counts[key]}" for key in sorted(counts)),
    ]
    for status in STATUSES:
        lines.append(f"{status}: {payload['legend']['validation_statuses'].get(status, 0)}")
    lines.append("reminder: canvas data is transient stdout/in-memory view-model data only.")
    return "\n".join(lines) + "\n"


def _display_node(node: dict[str, Any], overlays_by_target: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    graph_node_id = str(node.get("id", "node.unknown"))
    display_id = _display_id("node", graph_node_id)
    target_overlays = [
        *_target_matches(overlays_by_target, "node", graph_node_id),
        *_target_matches(overlays_by_target, "registry_entity", str(node.get("registry_ref", ""))),
        *_target_matches(overlays_by_target, "registry_entity", str(node.get("entity_ref", ""))),
    ]
    return {
        "id": display_id,
        "graph_node_id": graph_node_id,
        "label": str(node.get("label", graph_node_id)),
        "type": str(node.get("type", "artifact")),
        "category": str(node.get("category", "derived")),
        "source_refs": _source_refs(node.get("source_refs")),
        "annotations": _annotations(node.get("annotations")),
        "validation_overlays": _summaries(target_overlays),
    }


def _display_edge(edge: dict[str, Any], overlays_by_target: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    graph_edge_id = str(edge.get("id", "edge.unknown"))
    record = {
        "id": _display_id("edge", graph_edge_id),
        "graph_edge_id": graph_edge_id,
        "source": _display_id("node", str(edge.get("from", ""))),
        "target": _display_id("node", str(edge.get("to", ""))),
        "relation": str(edge.get("relation", "references")),
        "source_refs": _source_refs(edge.get("source_refs")),
        "validation_overlays": _summaries(_target_matches(overlays_by_target, "edge", graph_edge_id)),
    }
    label = edge.get("label")
    summary = edge.get("summary")
    if isinstance(label, str) and label:
        record["label"] = _trim(label, 120)
    if isinstance(summary, str) and summary:
        record["summary"] = _trim(summary, 180)
    return record


def _validation_overlays(compiled: CompilerResult, validation: ValidationRunResult) -> list[dict[str, Any]]:
    graph = _dict(compiled.graph_ir.get("graph"))
    records = [*_dict_items(graph.get("validation_attachments")), *_dict_items(validation.results)]
    for node in _dict_items(compiled.graph_ir.get("nodes")):
        records.extend(_dict_items(node.get("validation_attachments")))
    for edge in _dict_items(compiled.graph_ir.get("edges")):
        records.extend(_dict_items(edge.get("validation_attachments")))
    return [_overlay(record, index) for index, record in enumerate(sorted(records, key=lambda item: str(item.get("id", item.get("validation_ref", "")))))]


def _overlay(record: dict[str, Any], index: int) -> dict[str, Any]:
    target = _target_ref(record.get("target_ref"))
    status = str(record.get("status", "not_run"))
    overlay = {
        "id": f"overlay.{record.get('id', record.get('validation_ref', index))}",
        "validation_ref": str(record.get("validation_ref", record.get("id", ""))),
        "target": target,
        "check_type": str(record.get("check_type", "custom")),
        "status": status if status in STATUSES else "not_run",
        "messages": _messages(record.get("messages")),
        "source_refs": _source_refs(record.get("source_refs")),
    }
    return overlay


def _report_sections(report: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    summary = _dict(report.get("summary"))
    source_refs = _source_refs(report.get("source_refs"))
    sections = []
    for section in _sorted_dicts(report.get("sections")):
        sections.append(
            {
                "id": f"section.{kind}.{section.get('id', 'unknown')}",
                "report_ref": str(report.get("id", f"report.studio.{kind}")),
                "kind": kind,
                "title": str(section.get("title", section.get("id", "Section"))),
                "status": str(section.get("status", "not_run")),
                "summary": _trim(str(section.get("summary", summary.get("description", ""))), 240),
                "items": _section_items(section.get("items")),
                "source_refs": source_refs,
            }
        )
    return sections


def _legend(nodes: tuple[dict[str, Any], ...], overlays: list[dict[str, Any]]) -> dict[str, Any]:
    categories = sorted({node["category"] for node in nodes})
    return {
        "categories": [{"id": category, "label": category} for category in categories],
        "validation_statuses": {status: sum(1 for overlay in overlays if overlay["status"] == status) for status in STATUSES},
    }


def _display_id(kind: str, graph_id: str) -> str:
    return f"display.{kind}.{graph_id.removeprefix(f'{kind}.')}"


def _overlays_by_target(overlays: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for overlay in overlays:
        target = overlay["target"]
        grouped.setdefault((target["ref_type"], target["ref"]), []).append(overlay)
    return grouped


def _target_matches(grouped: dict[tuple[str, str], list[dict[str, Any]]], ref_type: str, ref: str) -> list[dict[str, Any]]:
    return sorted(grouped.get((ref_type, ref), []), key=lambda item: item["id"]) if ref else []


def _summaries(overlays: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"id": overlay["id"], "status": overlay["status"], "check_type": overlay["check_type"], "message_count": len(overlay["messages"]), "source_refs": overlay["source_refs"]} for overlay in overlays]


def _source_refs(value: Any) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for item in value if isinstance(value, (list, tuple)) else []:
        if isinstance(item, str) and item:
            refs.append({"ref_type": "path", "ref": item})
        elif isinstance(item, dict) and item.get("ref"):
            ref = {"ref_type": str(item.get("ref_type", "path")), "ref": str(item["ref"])}
            if isinstance(item.get("summary"), str) and item["summary"]:
                ref["summary"] = _trim(item["summary"], 180)
            refs.append(ref)
    return _unique_source_refs(refs)


def _unique_source_refs(refs: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for ref in refs:
        unique.setdefault((ref["ref_type"], ref["ref"]), ref)
    return [unique[key] for key in sorted(unique)]


def _target_ref(value: Any) -> dict[str, str]:
    target = _dict(value)
    return {"ref_type": str(target.get("ref_type", "canvas")), "ref": str(target.get("ref", CANVAS_ID))}


def _messages(value: Any) -> list[dict[str, str]]:
    messages = []
    for item in _dict_items(value):
        message = {"level": str(item.get("level", "info")), "text": _trim(str(item.get("text", "")), 500)}
        for key in ("path", "line", "column"):
            if key in item:
                message[key] = item[key]
        messages.append(message)
    return messages or [{"level": "info", "text": "Validation status available without copied evidence."}]


def _annotations(value: Any) -> list[dict[str, str]]:
    return [{"kind": str(item.get("kind", "note")), "text": _trim(str(item.get("text", "")), 500)} for item in _dict_items(value)]


def _section_items(value: Any) -> list[dict[str, Any]]:
    items = []
    for item in _dict_items(value):
        record = {"label": str(item.get("label", item.get("id", "")))}
        for key in ("value", "status"):
            if key in item:
                record[key] = item[key]
        items.append(record)
    return sorted(items, key=lambda item: str(item.get("label", "")))


def _sorted_dicts(value: Any) -> list[dict[str, Any]]:
    return sorted(_dict_items(value), key=lambda item: str(item.get("id", "")))


def _dict_items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, (list, tuple)) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _trim(value: str, limit: int) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."
