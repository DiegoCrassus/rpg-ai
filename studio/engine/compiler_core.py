"""Non-authoritative Studio compiler core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from studio.engine.reporting import build_report

REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    "studio/docs/contracts/compiler-validator-boundaries.md", "studio/docs/contracts/graph-ir-contract.md",
    "studio/docs/contracts/validation-result-ir-contract.md", "studio/engine/schemas/graph.schema.yaml",
    "studio/engine/schemas/workflow.schema.yaml", "studio/engine/schemas/validation-result.schema.yaml",
    ".sdlc/registry/index.yaml", ".sdlc/registry/sdlc-artifacts.yaml",
    ".sdlc/registry/cursor-artifacts.yaml", ".sdlc/registry/relationships.yaml",
    ".sdlc/sdlc.yaml", ".sdlc/process/lifecycle-model.yaml", ".sdlc/workflows/transitions.yaml",
    ".sdlc/process/master-workflow.md", ".sdlc/process/change-lifecycle.md",
    ".sdlc/runtime/manifest.yaml",
)

_NON_GOALS = {
    "graph": ("Does not replace .sdlc/, .cursor/, Plane, GitHub, or .sdlc/registry/.", "Does not execute workflows, commands, gates, agents, validators, or compilers.", "Does not store local tickets, backlog, specs, generated outputs, or durable evidence.", "Does not define UI, backend, frontend, API, database, deployment, or AI orchestration behavior."),
    "workflow": ("This workflow view does not execute stages, agents, commands, gates, or transitions.", "This workflow view does not update Plane, GitHub, .sdlc/, .cursor/, or registry state.", "This workflow view does not store local tickets, backlog, generated outputs, or durable evidence."),
    "report": ("No command runner, workflow runner, validator engine, or generated output persistence.", "No copied agent prompts, skill bodies, rule bodies, hook logic, templates, lifecycle prose, CI logs, or evidence.", "No replacement behavior for .sdlc/, .cursor/, .sdlc/registry/, Plane, or GitHub."),
}
_EXCLUDED_SOURCE_AREAS = ("app/", "studio/engine/examples/", "studio/engine/generated/", "specs/", "local tickets", "local backlog", "local evidence files", "generated Graph IR, Workflow IR, reports, validation, snapshots, and command outputs")
_GRAPH_NODE_TYPES = {"workflow", "stage", "agent", "skill", "command", "gate", "policy", "template", "hook", "rule", "module", "registry_entity", "registry_relationship", "validation", "artifact", "external_authority"}
_KIND_TO_NODE_TYPE = {
    "agent": "agent", "command": "command", "doctor": "validation", "gate": "gate",
    "gateway_policy": "policy", "hook": "hook", "module": "module", "rule": "rule",
    "script": "command", "skill": "skill", "stage": "stage", "template": "template",
    "workflow": "workflow", "workboard_policy": "policy",
}
_WORKFLOW_SOURCES = (
    ".sdlc/process/lifecycle-model.yaml",
    ".sdlc/workflows/transitions.yaml",
    ".sdlc/runtime/manifest.yaml",
    ".sdlc/process/master-workflow.md",
    ".sdlc/process/change-lifecycle.md",
    "studio/engine/schemas/workflow.schema.yaml",
)


@dataclass(frozen=True)
class CompilerResult:
    """In-memory compiler result."""

    graph_ir: dict[str, Any]
    workflow_ir: dict[str, Any]
    report: dict[str, Any]


class CompilerInputError(RuntimeError):
    """Raised when required compiler inputs are missing or unreadable."""

    def __init__(
        self,
        *,
        missing_paths: list[str] | None = None,
        unreadable_yaml: dict[str, str] | None = None,
        unreadable_paths: dict[str, str] | None = None,
    ) -> None:
        self.missing_paths = sorted(missing_paths or [])
        self.unreadable_yaml = dict(sorted((unreadable_yaml or {}).items()))
        self.unreadable_paths = dict(sorted((unreadable_paths or {}).items()))
        super().__init__(self._message())

    def _message(self) -> str:
        groups = (
            ("Missing required compiler inputs", self.missing_paths),
            ("Unreadable required YAML", self.unreadable_yaml),
            ("Unreadable required compiler inputs", self.unreadable_paths),
        )
        parts: list[str] = []
        for label, values in groups:
            if isinstance(values, dict) and values:
                parts.append(f"{label}: " + ", ".join(f"{path} ({error})" for path, error in values.items()))
            elif values:
                parts.append(f"{label}: " + ", ".join(values))
        return "; ".join(parts) or "Invalid compiler inputs"


def compile_studio_sources(root: Path | str) -> CompilerResult:
    """Compile Studio Graph IR, Workflow IR, and report records in memory."""

    repo_root = Path(root)
    required_paths = _validate_required_inputs(repo_root)
    yaml_inputs = _load_required_yaml(repo_root, required_paths)
    sdlc_artifacts = _items(yaml_inputs, ".sdlc/registry/sdlc-artifacts.yaml", "artifacts")
    cursor_artifacts = _items(yaml_inputs, ".sdlc/registry/cursor-artifacts.yaml", "artifacts")
    relationships = _items(yaml_inputs, ".sdlc/registry/relationships.yaml", "relationships")
    model = yaml_inputs.get(".sdlc/process/lifecycle-model.yaml") or {}
    stages = model.get("stages") if isinstance(model.get("stages"), list) else []
    model_transitions = model.get("transitions") if isinstance(model.get("transitions"), list) else []
    overlay = _items(yaml_inputs, ".sdlc/workflows/transitions.yaml", "workflows")
    transitions = _merge_transitions(model_transitions, overlay)
    artifacts = [*sdlc_artifacts, *cursor_artifacts]
    return CompilerResult(
        _build_graph_ir(artifacts, relationships),
        _build_workflow_ir(stages, transitions),
        _build_report(repo_root, required_paths, artifacts, relationships, stages, transitions),
    )


def _validate_required_inputs(root: Path) -> tuple[str, ...]:
    missing = [path for path in REQUIRED_SOURCE_PATHS if not (root / path).is_file()]
    if missing:
        raise CompilerInputError(missing_paths=missing)
    unreadable: dict[str, str] = {}
    for path in REQUIRED_SOURCE_PATHS:
        try:
            (root / path).read_text(encoding="utf-8")
        except OSError as exc:
            unreadable[path] = exc.strerror or exc.__class__.__name__
        except UnicodeError as exc:
            unreadable[path] = exc.__class__.__name__
    if unreadable:
        raise CompilerInputError(unreadable_paths=unreadable)
    return REQUIRED_SOURCE_PATHS


def _load_required_yaml(root: Path, required_paths: tuple[str, ...]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    unreadable: dict[str, str] = {}
    for path in (path for path in required_paths if path.endswith((".yaml", ".yml"))):
        try:
            parsed = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            unreadable[path] = str(exc).splitlines()[0]
        else:
            loaded[path] = parsed if isinstance(parsed, dict) else {}
    if unreadable:
        raise CompilerInputError(unreadable_yaml=unreadable)
    return loaded


def _build_graph_ir(artifacts: list[dict[str, Any]], relationships: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [_artifact_to_node(item) for item in sorted(artifacts, key=lambda item: str(item.get("id", "")))]
    node_ids = {node["registry_ref"]: node["id"] for node in nodes}
    edges = [_relationship_to_edge(item, node_ids) for item in sorted(relationships, key=lambda item: str(item.get("id", ""))) if item.get("from") in node_ids and item.get("to") in node_ids]
    refs = (
        (".sdlc/registry/sdlc-artifacts.yaml", "SDLC registry nodes"),
        (".sdlc/registry/cursor-artifacts.yaml", "Cursor registry nodes"),
        (".sdlc/registry/relationships.yaml", "Registry graph edges"),
        ("studio/engine/schemas/graph.schema.yaml", "Graph IR schema"),
        ("studio/docs/contracts/graph-ir-contract.md", "Graph IR contract"),
    )
    return {"graph": {"id": "graph.sdlc_studio.registry", "name": "SDLC Studio Registry Graph", "description": "Derived, non-executable graph over SDLC and Cursor registry records.", "version": "0.1.0", "source_refs": [_source_ref(*ref) for ref in refs], "non_goals": list(_NON_GOALS["graph"])}, "nodes": nodes, "edges": edges}


def _artifact_to_node(artifact: dict[str, Any]) -> dict[str, Any]:
    artifact_id = str(artifact.get("id", "unknown"))
    kind = str(artifact.get("kind", "artifact"))
    source_system = str(artifact.get("source_system", "derived"))
    summary = str(artifact.get("summary", "")).strip()
    node = {
        "id": f"node.{artifact_id}",
        "type": _KIND_TO_NODE_TYPE.get(kind, kind if kind in _GRAPH_NODE_TYPES else "artifact"),
        "category": source_system if source_system in {"sdlc", "cursor"} else "derived",
        "label": _trim(str(artifact.get("name", artifact_id)), 120),
        "registry_ref": artifact_id,
        "entity_ref": artifact_id,
        "source_refs": [_source_ref(str(artifact.get("path", "")), _trim(summary, 180))],
    }
    if summary:
        node["annotations"] = [{"kind": "note", "text": _trim(summary, 500)}]
    return node


def _relationship_to_edge(relationship: dict[str, Any], node_ids: dict[str, str]) -> dict[str, Any]:
    summary = str(relationship.get("summary", "")).strip()
    edge = {
        "id": f"edge.{relationship.get('id', 'unknown')}",
        "from": node_ids[str(relationship["from"])],
        "to": node_ids[str(relationship["to"])],
        "relation": str(relationship.get("relation", "references")),
        "source_refs": [_source_ref(str(path), "Registry relationship source") for path in _as_list(relationship.get("source_refs"))],
    }
    if summary:
        edge["summary"] = _trim(summary, 180)
    return edge


def _merge_transitions(
    model_transitions: list[dict[str, Any]],
    overlay_workflows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Graph from lifecycle-model; metadata from transitions.yaml overlay."""

    overlay_by_id = {
        str(item.get("id")): item
        for item in overlay_workflows
        if isinstance(item, dict) and item.get("id")
    }
    merged: list[dict[str, Any]] = []
    for base in model_transitions:
        if not isinstance(base, dict) or not base.get("id"):
            continue
        tid = str(base["id"])
        item = dict(base)
        if overlay := overlay_by_id.get(tid):
            for key in ("name", "description", "agent", "skill", "preconditions", "outputs"):
                if overlay.get(key) and not item.get(key):
                    item[key] = overlay[key]
            item["_overlay"] = True
        merged.append(item)
    return merged


def _build_workflow_ir(stages: list[dict[str, Any]], transitions: list[dict[str, Any]]) -> dict[str, Any]:
    stage_records = [_stage_to_record(stage) for stage in sorted(stages, key=_stage_key)]
    transition_records = [_transition_to_record(item) for item in sorted(transitions, key=lambda item: str(item.get("id", "")))]
    return {"workflow": {"id": "workflow.sdlc.lifecycle", "name": "SDLC Lifecycle Workflow", "description": "Derived, non-executable workflow view assembled from SDLC lifecycle and transition sources.", "source_refs": list(_WORKFLOW_SOURCES), "stages": stage_records, "transitions": transition_records, "non_goals": list(_NON_GOALS["workflow"])}}


def _stage_to_record(stage: dict[str, Any]) -> dict[str, Any]:
    stage_id = str(stage.get("id", "unknown"))
    return {
        "id": f"stage.{stage_id}",
        "name": _trim(str(stage.get("name", stage_id)), 120),
        "stage_ref": f"sdlc.stage.lifecycle#{stage_id}",
        "description": _trim(str(stage.get("description", "")), 240),
        "order": stage.get("order"),
        "source_refs": [".sdlc/process/lifecycle-model.yaml"],
    }


def _transition_to_record(transition: dict[str, Any]) -> dict[str, Any]:
    transition_id = str(transition.get("id", "unknown"))
    source_refs = [".sdlc/process/lifecycle-model.yaml"]
    if transition.get("_overlay"):
        source_refs.append(".sdlc/workflows/transitions.yaml")
    record = {
        "id": f"transition.{transition_id}",
        "name": _trim(str(transition.get("name", transition_id)), 120),
        "from": f"stage.{transition.get('from_stage', '')}",
        "to": f"stage.{transition.get('to_stage', '')}",
        "relation": "recovery" if transition_id == "incident_to_autofix" else "next",
        "source_refs": source_refs,
    }
    agent = transition.get("agent")
    skill = transition.get("skill")
    description = str(transition.get("description", "")).strip()
    if agent:
        record["agent_ref"] = f"cursor.agent.{str(agent).replace('-', '_')}"
    if skill:
        record["skill_refs"] = [f"cursor.skill.{str(skill).replace('-', '_')}"]
    if description:
        record["description"] = _trim(description, 240)
    return record


def _build_report(root: Path, required_paths: tuple[str, ...], artifacts: list[dict[str, Any]], relationships: list[dict[str, Any]], stages: list[dict[str, Any]], transitions: list[dict[str, Any]]) -> dict[str, Any]:
    registry_ids = {str(artifact.get("id")) for artifact in artifacts}
    unresolved = sorted(str(item.get("id", "unknown")) for item in relationships if item.get("from") not in registry_ids or item.get("to") not in registry_ids)
    missing_optional_paths = _missing_optional_paths(root, required_paths, artifacts, relationships)
    status = "pass" if not unresolved else "warn"
    counts = {
        "graph_edges": len(relationships),
        "graph_nodes": len(artifacts),
        "missing_optional_source_paths": len(missing_optional_paths),
        "required_inputs": len(required_paths),
        "unresolved_relationships": len(unresolved),
        "workflow_stages": len(stages),
        "workflow_transitions": len(transitions),
    }
    return build_report(
        report_id="report.studio.compile",
        kind="compile",
        status=status,
        summary={"description": "Compiled Graph IR and Workflow IR in memory.", "counts": counts},
        sections=[
            {
                "id": "coverage",
                "title": "Coverage",
                "status": status,
                "items": [{"label": key, "value": value} for key, value in counts.items()],
            },
            {
                "id": "boundaries",
                "title": "Boundaries",
                "status": "pass",
                "items": [{"label": "excluded_source_area", "value": path} for path in _EXCLUDED_SOURCE_AREAS],
            },
            {
                "id": "unresolved_relationships",
                "title": "Unresolved Relationships",
                "status": "warn" if unresolved else "pass",
                "items": [{"label": relationship_id, "value": "unresolved"} for relationship_id in unresolved],
            },
            {
                "id": "missing_optional_source_paths",
                "title": "Missing Optional Source Paths",
                "status": "warn" if missing_optional_paths else "pass",
                "items": [{"label": path, "value": "missing"} for path in missing_optional_paths],
            },
        ],
        source_refs=list(required_paths),
        non_goals=list(_NON_GOALS["report"]),
    )


def _missing_optional_paths(root: Path, required_paths: tuple[str, ...], artifacts: list[dict[str, Any]], relationships: list[dict[str, Any]]) -> list[str]:
    referenced = {str(artifact.get("path", "")) for artifact in artifacts if str(artifact.get("path", "")).strip()}
    for relationship in relationships:
        referenced.update(str(path) for path in _as_list(relationship.get("source_refs")))
    return sorted(path for path in referenced if path not in set(required_paths) and not (root / path).exists())


def _items(data: dict[str, Any], path: str, key: str) -> list[dict[str, Any]]:
    value = data[path].get(key)
    return value if isinstance(value, list) else []


def _source_ref(ref: str, summary: str = "") -> dict[str, str]:
    source_ref = {"ref_type": "path", "ref": ref}
    if summary:
        source_ref["summary"] = _trim(summary, 180)
    return source_ref


def _stage_key(stage: dict[str, Any]) -> tuple[int, str]:
    order = stage.get("order")
    return (order if isinstance(order, int) else 10_000, str(stage.get("id", "")))


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _trim(value: str, limit: int) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."
