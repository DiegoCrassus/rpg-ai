"""Workflow builder canvas: lifecycle stages and transitions (not registry stage artifacts)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from studio.engine.compiler_core import CompilerInputError, compile_studio_sources
from studio_service.api.errors import StudioApiError


def build_workflow_builder_canvas(root: Path) -> dict[str, Any]:
    """Project workflow_ir stages/transitions into canvas node/edge records for the builder UI."""

    try:
        compiled = compile_studio_sources(root)
    except CompilerInputError as exc:
        raise StudioApiError(
            422,
            "COMPILER_INPUT_ERROR",
            "Required compiler inputs are missing or unreadable",
            details={
                "missing_paths": exc.missing_paths,
                "unreadable_yaml": exc.unreadable_yaml,
                "unreadable_paths": exc.unreadable_paths,
            },
        ) from exc

    workflow = (compiled.workflow_ir or {}).get("workflow") or {}
    stages = list(workflow.get("stages") or [])
    transitions = list(workflow.get("transitions") or [])

    nodes = [_stage_to_canvas_node(stage) for stage in sorted(stages, key=_stage_sort_key)]
    display_by_stage = {
        str(stage.get("id", "")): node["id"] for stage, node in zip(stages, nodes, strict=False)
    }

    edges: list[dict[str, Any]] = []
    for transition in transitions:
        from_stage = str(transition.get("from", ""))
        to_stage = str(transition.get("to", ""))
        source = display_by_stage.get(from_stage)
        target = display_by_stage.get(to_stage)
        if not source or not target:
            continue
        transition_id = str(transition.get("id", "transition.unknown"))
        slug = transition_id.removeprefix("transition.")
        agent_ref = str(transition.get("agent_ref", ""))
        agent_slug = agent_ref.removeprefix("cursor.agent.").replace("_", "-") if agent_ref else ""
        skill_refs = transition.get("skill_refs") or []
        skill_slug = ""
        if skill_refs:
            raw_skill = str(skill_refs[0])
            skill_slug = raw_skill.removeprefix("cursor.skill.").replace("_", "-")

        edges.append(
            {
                "id": f"display.edge.{slug}",
                "graph_edge_id": transition_id,
                "source": source,
                "target": target,
                "relation": "transitions_to",
                "source_refs": [{"ref_type": "path", "ref": ".sdlc/workflows/transitions.yaml"}],
                "validation_overlays": [],
                "label": str(transition.get("name", transition_id)),
                "summary": str(transition.get("description", "")),
                "agent": agent_slug,
                "skill": skill_slug,
            }
        )

    return {
        "canvas": {
            "id": "canvas.sdlc_studio.workflow_builder",
            "name": "SDLC Lifecycle Workflow Builder",
            "version": "0.1.0",
            "authority": "derived_non_authoritative",
            "source_refs": [
                {"ref_type": "path", "ref": ".sdlc/stages/lifecycle.yaml"},
                {"ref_type": "path", "ref": ".sdlc/workflows/transitions.yaml"},
            ],
            "non_goals": [
                "Does not apply patches; use POST /studio/proposals from the UI.",
            ],
        },
        "nodes": nodes,
        "edges": edges,
        "overlays": [],
        "sections": [],
        "legend": {
            "categories": [{"id": "sdlc", "label": "sdlc"}],
            "validation_statuses": {"pass": 0, "warn": 0, "fail": 0, "not_run": len(nodes)},
        },
        "filters": {
            "section": None,
            "validation_status": None,
            "entity_type": None,
            "q": None,
        },
        "meta": {
            "total_nodes": len(nodes),
            "filtered_nodes": len(nodes),
            "total_edges": len(edges),
            "filtered_edges": len(edges),
        },
    }


def _stage_sort_key(stage: dict[str, Any]) -> tuple[int, str]:
    order = stage.get("order")
    if isinstance(order, int):
        return (order, str(stage.get("id", "")))
    return (999, str(stage.get("id", "")))


def _stage_to_canvas_node(stage: dict[str, Any]) -> dict[str, Any]:
    stage_id = str(stage.get("id", "stage.unknown"))
    slug = stage_id.removeprefix("stage.")
    return {
        "id": f"display.node.{stage_id}",
        "graph_node_id": f"node.{stage_id}",
        "label": str(stage.get("name", slug)),
        "type": "stage",
        "category": "sdlc",
        "source_refs": [{"ref_type": "path", "ref": ".sdlc/stages/lifecycle.yaml"}],
        "annotations": [],
        "validation_overlays": [],
    }
