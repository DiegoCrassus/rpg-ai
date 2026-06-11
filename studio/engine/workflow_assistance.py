"""Derived, non-authoritative workflow assistance advisory projection."""

from typing import Any

from studio.engine.canvas_view_model import CanvasViewModel, build_canvas_view_model
from studio.engine.compiler_core import CompilerResult, compile_studio_sources
from studio.engine.reporting import AUTHORITY
from studio.engine.validation_inspection import (
    _path_refs,
    _source_refs,
    _trim,
    _unique_source_refs,
    build_validation_inspection_model,
)
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

ASSISTANCE_ID = "assistance.sdlc_studio.workflow"
ASSISTANCE_SOURCE_PATHS = (
    "studio/engine/workflow_assistance.py",
    "studio/docs/prototypes/ai-composition-guardrails.md",
    "studio/docs/prototypes/ai-workflow-assistance-prototype.md",
    "docs/roadmap/sdlc-studio-mvp-roadmap.md",
)
VALID_SUGGESTION_KINDS = (
    "validation_gap",
    "missing_source_ref",
    "workflow_handoff",
    "plane_follow_up_draft",
    "risk_summary",
)
ASSISTANCE_NON_GOALS = (
    "Does not invoke LLMs, agents, MCP, shell, workflow execution, or Plane/GitHub mutation.",
    "Does not persist outputs, generate files, or present advisory data as QA evidence or gate results.",
    "Does not copy authoritative rule bodies, prompts, CI logs, or evidence into suggestions.",
)
PLANE_DRAFT_REMINDER = "Create or update a Plane card; do not apply from Studio output."


class WorkflowAssistanceInputError(ValueError):
    """Raised for unsupported suggestion kind filters."""


def build_workflow_assistance_from_sources(root: Any, *, kind: str | None = None) -> dict[str, Any]:
    """Compile, validate, derive canvas/inspection data, and build assistance in memory."""

    compiled = compile_studio_sources(root)
    validation = validate_compiler_result(compiled, root)
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    return build_workflow_assistance_model(compiled, validation, canvas, inspection, kind=kind)


def build_workflow_assistance_model(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    canvas: CanvasViewModel,
    inspection: dict[str, Any],
    *,
    kind: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic advisory assistance model from existing derived records."""

    if kind is not None and kind not in VALID_SUGGESTION_KINDS:
        raise WorkflowAssistanceInputError(f"invalid kind: {kind}")

    canvas_dict = canvas.to_dict()
    all_suggestions = _build_suggestions(compiled, canvas_dict, inspection)
    visible = tuple(item for item in all_suggestions if kind is None or item["kind"] == kind)
    explanations = sorted(_build_explanations(compiled, validation, canvas_dict, inspection), key=lambda item: item["id"])
    insp_summary = inspection["summary"]
    workflow = _dict(compiled.workflow_ir.get("workflow"))
    fail_count = insp_summary["by_status"].get("fail", 0)
    return {
        "assistance": {
            "id": ASSISTANCE_ID,
            "authority": AUTHORITY,
            "guardrails_ref": "studio/docs/prototypes/ai-composition-guardrails.md",
            "prototype_ref": "studio/docs/prototypes/ai-workflow-assistance-prototype.md",
            "freshness": "derived_inputs_only",
            "source_refs": _unique_source_refs(
                [*_path_refs(ASSISTANCE_SOURCE_PATHS), *_source_refs(compiled.report.get("source_refs")), *_source_refs(validation.report.get("source_refs"))]
            ),
            "non_goals": list(ASSISTANCE_NON_GOALS),
            "filters": {"kind": kind},
        },
        "summary": {
            "workflow_stages": len(_items(workflow.get("stages"))),
            "workflow_transitions": len(_items(workflow.get("transitions"))),
            "validation_total": insp_summary["total_records"],
            "validation_fail": fail_count,
            "validation_warn": insp_summary["by_status"].get("warn", 0),
            "suggestion_count": len(visible),
            "explanation_count": len(explanations),
        },
        "explanations": explanations,
        "suggestions": list(visible),
        "annotations": _build_annotations(compiled, canvas_dict),
    }


def render_workflow_assistance_text(model: dict[str, Any]) -> str:
    """Render a concise stdout-only workflow assistance summary."""

    assistance, summary = model["assistance"], model["summary"]
    lines = [
        "Studio workflow assistance: derived, non-authoritative output",
        f"assistance: {assistance['id']}",
        f"authority: {assistance['authority']}",
        f"freshness: {assistance['freshness']}",
        f"guardrails: {assistance['guardrails_ref']}",
        f"filters: {'kind=' + assistance['filters']['kind'] if assistance['filters']['kind'] else 'none'}",
        *(f"{key.replace('_', ' ')}: {summary[key]}" for key in sorted(summary)),
        "explanations:",
        *(f"- {item['id']} [{item['kind']}] {item['summary']}" for item in model["explanations"]),
        "suggestions:",
    ]
    for item in model["suggestions"]:
        lines.extend(
            [
                f"- {item['id']} [{item['kind']}/{item['status']}] {item['summary']}",
                f"  observed: {item['observed']}",
                f"  proposed: {item['proposed']}",
            ]
        )
    lines.append("reminder: assistance data is derived, non-authoritative, and derived_inputs_only only.")
    lines.append("reminder: suggestions are advisory; create or update Plane cards manually.")
    return "\n".join(lines) + "\n"


def _build_explanations(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    canvas_dict: dict[str, Any],
    inspection: dict[str, Any],
) -> list[dict[str, Any]]:
    workflow = _dict(compiled.workflow_ir.get("workflow"))
    by_status = inspection["summary"]["by_status"]
    canvas = canvas_dict["canvas"]
    return [
        {"id": "assistance.explanation.canvas_overview", "kind": "canvas_overview", "summary": _trim(f"Canvas {canvas.get('id', 'canvas.unknown')} projects {len(canvas_dict.get('nodes', []))} nodes and {len(canvas_dict.get('edges', []))} edges with derived overlays.", 240), "source_refs": _unique_source_refs([*_path_refs(("studio/docs/contracts/visual-orchestration-prototype.md",)), *_source_refs(canvas.get("source_refs"))])},
        {"id": "assistance.explanation.validation_overview", "kind": "validation_overview", "summary": _trim(f"Validation inspection reports {inspection['summary']['total_records']} records: {by_status.get('pass', 0)} pass, {by_status.get('warn', 0)} warn, {by_status.get('fail', 0)} fail.", 240), "source_refs": _unique_source_refs([*_path_refs(("studio/docs/contracts/validation-result-ir-contract.md",)), *_source_refs(validation.report.get("source_refs"))])},
        {"id": "assistance.explanation.workflow_structure", "kind": "workflow_structure", "summary": _trim(f"Workflow view lists {len(_items(workflow.get('stages')))} stages and {len(_items(workflow.get('transitions')))} transitions from derived IR.", 240), "source_refs": _unique_source_refs([*_path_refs(("studio/engine/schemas/workflow.schema.yaml",)), *_source_refs(workflow.get("source_refs"))])},
    ]


def _build_suggestions(compiled: CompilerResult, canvas_dict: dict[str, Any], inspection: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    suggestions: list[dict[str, Any]] = []
    suggestions.extend(_validation_gap_suggestions(inspection))
    suggestions.extend(_missing_source_ref_suggestions(compiled))
    suggestions.extend(_workflow_handoff_suggestions(compiled))
    suggestions.extend(_risk_summary_suggestions(canvas_dict, inspection))
    draft = _plane_follow_up_draft(compiled, inspection)
    if draft is not None:
        suggestions.append(draft)
    return tuple(sorted(suggestions, key=lambda item: item["id"]))


def _validation_gap_suggestions(inspection: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for record in inspection["records"]:
        if record["status"] not in ("fail", "warn"):
            continue
        ref = record["validation_ref"]
        target = record["target"]
        out.append(
            _suggestion(
                f"assistance.suggestion.validation_gap.{ref.removeprefix('validation.')}",
                "validation_gap",
                f"Review {record['status']} validation for {target['ref_type']}:{target['ref']}.",
                f"{ref} reports {record['status']} via {record['check_type']}: {record['summary']}",
                "Open or update a Plane-scoped card to address this validation gap; do not apply fixes from Studio output.",
                [{"ref_type": "validation", "ref": ref}, *record["source_refs"]],
            )
        )
    return out


def _missing_source_ref_suggestions(compiled: CompilerResult) -> list[dict[str, Any]]:
    out = []
    for section in _items(compiled.report.get("sections")):
        section_id = str(section.get("id", ""))
        if section_id not in ("unresolved_relationships", "missing_optional_source_paths"):
            continue
        for item in _items(section.get("items")):
            label = str(item.get("label", "unknown"))
            out.append(
                _suggestion(
                    f"assistance.suggestion.missing_source_ref.{section_id}.{label.replace('/', '_').replace('.', '_')}",
                    "missing_source_ref",
                    f"Compile report lists unresolved reference: {label}.",
                    f"Section {section_id} marks {label} as {item.get('value', 'unresolved')}.",
                    "Verify source path or registry relationship in authoritative `.sdlc/` artifacts.",
                    [{"ref_type": "path", "ref": "studio/engine/compiler_core.py"}, {"ref_type": "report_section", "ref": f"report.studio.compile#{section_id}"}],
                )
            )
    return out


def _workflow_handoff_suggestions(compiled: CompilerResult) -> list[dict[str, Any]]:
    workflow = _dict(compiled.workflow_ir.get("workflow"))
    stage_ids = {str(stage.get("id", "")) for stage in _items(workflow.get("stages"))}
    workflow_refs = _source_refs(workflow.get("source_refs"))
    out = []
    for stage in _items(workflow.get("stages")):
        stage_id = str(stage.get("id", "stage.unknown"))
        if stage.get("agent_ref"):
            continue
        out.append(
            _suggestion(
                f"assistance.suggestion.workflow_handoff.{stage_id.removeprefix('stage.')}_no_agent",
                "workflow_handoff",
                f"Stage {stage_id} has no agent_ref in derived workflow IR.",
                f"{stage_id} ({stage.get('name', stage_id)}) lacks an explicit agent_ref assignment.",
                "Review lifecycle YAML and transition agent mappings for human/agent handoff clarity.",
                [{"ref_type": "stage", "ref": stage_id}, *workflow_refs, *_source_refs(stage.get("source_refs"))],
            )
        )
    for transition in _items(workflow.get("transitions")):
        transition_id = str(transition.get("id", "transition.unknown"))
        for endpoint in ("from", "to"):
            target = str(transition.get(endpoint, ""))
            if target and target not in stage_ids:
                stable = transition_id.removeprefix("transition.")
                out.append(
                    _suggestion(
                        f"assistance.suggestion.workflow_handoff.{stable}_{endpoint}_orphan",
                        "workflow_handoff",
                        f"Transition {transition_id} references missing stage {target}.",
                        f"{transition_id} {endpoint} target {target} not found among {len(stage_ids)} stages.",
                        "Align transition endpoints with lifecycle stage IDs in `.sdlc/workflows/transitions.yaml`.",
                        [{"ref_type": "transition", "ref": transition_id}, {"ref_type": "stage", "ref": target}, *workflow_refs],
                    )
                )
    return out


def _risk_summary_suggestions(canvas_dict: dict[str, Any], inspection: dict[str, Any]) -> list[dict[str, Any]]:
    canvas_fail = canvas_dict["legend"]["validation_statuses"].get("fail", 0)
    inspection_fail = inspection["summary"]["by_status"].get("fail", 0)
    if canvas_fail <= 0 and inspection_fail <= 0:
        return []
    canvas_id = str(canvas_dict["canvas"].get("id", "canvas.unknown"))
    return [
        _suggestion(
            "assistance.suggestion.risk_summary.validation_failures",
            "risk_summary",
            f"Derived validation reports {inspection_fail} fail overlay(s) on canvas.",
            f"Canvas legend fail={canvas_fail}; inspection by_status fail={inspection_fail}.",
            "Prioritize Plane-scoped remediation of failing validation records before downstream gates.",
            [{"ref_type": "canvas", "ref": canvas_id}, {"ref_type": "path", "ref": "studio/engine/validation_inspection.py"}],
        )
    ]


def _plane_follow_up_draft(compiled: CompilerResult, inspection: dict[str, Any]) -> dict[str, Any] | None:
    fail_count = inspection["summary"]["by_status"].get("fail", 0)
    compile_status = str(compiled.report.get("status", "pass"))
    if fail_count <= 0 and compile_status not in ("warn", "fail"):
        return None
    note = f" compile_status={compile_status}" if compile_status in ("warn", "fail") else ""
    return _suggestion(
        "assistance.suggestion.plane_follow_up_draft.aggregate",
        "plane_follow_up_draft",
        f"Aggregate follow-up suggested after {fail_count} validation failure(s).{note}",
        f"Inspection reports fail={fail_count}, warn={inspection['summary']['by_status'].get('warn', 0)}.",
        "Draft a Plane card scope for human review; Studio does not create or update cards.",
        [{"ref_type": "path", "ref": "studio/docs/prototypes/ai-composition-guardrails.md"}],
        draft={
            "title_hint": "[SDLC Studio] Address derived validation gaps",
            "scope_hint": "Review failing validation records and compile report warnings from Studio derived outputs.",
            "acceptance_hint": "Validation fail count returns to zero after authoritative fixes on feature branch.",
            "reminder": PLANE_DRAFT_REMINDER,
        },
    )


def _build_annotations(compiled: CompilerResult, canvas_dict: dict[str, Any]) -> list[dict[str, Any]]:
    annotations = []
    for node in _items(canvas_dict.get("nodes"))[:2]:
        annotations.append(
            {
                "id": f"assistance.annotation.canvas_node.{node['id'].removeprefix('display.node.')}",
                "target_ref": {"ref_type": "canvas_node", "ref": node["id"]},
                "annotation": _trim(f"Derived node label: {node.get('label', node['id'])} ({node.get('type', 'artifact')}).", 240),
                "source_refs": _unique_source_refs(_source_refs(node.get("source_refs")) or [{"ref_type": "path", "ref": "studio/engine/canvas_view_model.py"}]),
            }
        )
    for stage in _items(_dict(compiled.workflow_ir.get("workflow")).get("stages"))[:1]:
        stage_id = str(stage.get("id", "stage.unknown"))
        annotations.append(
            {
                "id": f"assistance.annotation.workflow_stage.{stage_id.removeprefix('stage.')}",
                "target_ref": {"ref_type": "stage", "ref": stage_id},
                "annotation": _trim(f"Derived stage: {stage.get('name', stage_id)}.", 240),
                "source_refs": _unique_source_refs(_source_refs(stage.get("source_refs"))),
            }
        )
    return annotations[:3]


def _suggestion(
    sid: str,
    kind: str,
    summary: str,
    observed: str,
    proposed: str,
    source_refs: list[dict[str, str]],
    *,
    draft: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "id": sid,
        "kind": kind,
        "status": "advisory",
        "summary": _trim(summary, 240),
        "observed": _trim(observed, 240),
        "proposed": _trim(proposed, 240),
        "source_refs": _unique_source_refs(source_refs),
        "plane_follow_up_draft": draft,
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
