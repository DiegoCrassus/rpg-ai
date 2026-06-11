"""Derived, non-executing SDLC lifecycle simulation preview projection."""

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

SIMULATION_ID = "simulation.sdlc_studio.preview"
SIMULATION_SOURCE_PATHS = (
    "studio/engine/simulation_preview.py",
    "studio/docs/prototypes/ai-simulation-preview-prototype.md",
    "docs/roadmap/sdlc-studio-mvp-roadmap.md",
    ".sdlc/process/change-lifecycle.md",
    ".sdlc/process/master-workflow.md",
)
VALID_SCENARIOS = (
    "docs_only",
    "feature_implementation",
    "qa_failure",
    "reviewer_escalation",
    "devops_finish",
)
VALID_INTENTS = ("DOCS_ONLY", "FEATURE")
VALID_PATH_LABELS = ("expected", "blocked", "unsupported")
VALID_STEP_KINDS = ("handoff", "stage", "transition")
VALID_TAGS = (
    "docs_scope",
    "failure_path",
    "finish_flow",
    "gate_blocked",
    "happy_path",
    "human_escalation",
)
_TRANSITION_YAML = ".sdlc/workflows/transitions.yaml#"
_TRANSITION_KEYS = (
    "requirements_to_architecture",
    "architecture_to_implementation",
    "implementation_to_validation",
    "validation_to_review",
    "review_to_deployment",
    "deployment_to_observability",
    "incident_to_autofix",
)
TRANSITION_LIFECYCLE_SOURCES = {f"transition.{key}": f"{_TRANSITION_YAML}{key}" for key in _TRANSITION_KEYS}
SIMULATION_NON_GOALS = ("Non-executing preview only; see studio/docs/prototypes/ai-simulation-preview-prototype.md.",)


class SimulationPreviewInputError(ValueError):
    pass


def build_simulation_preview_from_sources(
    root: Any,
    *,
    scenario: str | None = None,
    intent: str | None = None,
    path_label: str | None = None,
    step_kind: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    compiled = compile_studio_sources(root)
    validation = validate_compiler_result(compiled, root)
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    return build_simulation_preview_model(
        compiled,
        validation,
        canvas,
        inspection,
        scenario=scenario,
        intent=intent,
        path_label=path_label,
        step_kind=step_kind,
        tag=tag,
    )


def build_simulation_preview_model(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    canvas: CanvasViewModel,
    inspection: dict[str, Any],
    *,
    scenario: str | None = None,
    intent: str | None = None,
    path_label: str | None = None,
    step_kind: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    filters = _validated_filters(
        scenario=scenario,
        intent=intent,
        path_label=path_label,
        step_kind=step_kind,
        tag=tag,
    )

    transitions = _transition_index(compiled)
    fail_count = inspection["summary"]["by_status"].get("fail", 0)
    all_scenarios = tuple(_build_scenario(sid, compiled, transitions, fail_count) for sid in VALID_SCENARIOS)
    visible = _apply_scenario_filters(all_scenarios, filters)
    path_counts = _path_label_counts(visible)
    return {
        "simulation": {
            "id": SIMULATION_ID,
            "authority": AUTHORITY,
            "execution_mode": "non_executing_preview",
            "prototype_ref": "studio/docs/prototypes/ai-simulation-preview-prototype.md",
            "freshness": "derived_inputs_only",
            "source_refs": _unique_source_refs(
                [*_path_refs(SIMULATION_SOURCE_PATHS), *_source_refs(compiled.report.get("source_refs")), *_source_refs(validation.report.get("source_refs"))]
            ),
            "non_goals": list(SIMULATION_NON_GOALS),
            "lifecycle_authority": list(SIMULATION_SOURCE_PATHS[3:5]),
            "filters": filters,
        },
        "summary": {
            "scenario_count": len(visible),
            "step_count": sum(len(item["steps"]) for item in visible),
            "path_labels": path_counts,
            "validation_fail": fail_count,
            "validation_warn": inspection["summary"]["by_status"].get("warn", 0),
            "workflow_transitions": len(transitions),
            "canvas_ref": str(canvas.canvas.get("id", "canvas.unknown")),
        },
        "scenarios": list(visible),
        "lifecycle_map": _build_lifecycle_map(transitions),
    }


def render_simulation_preview_text(model: dict[str, Any]) -> str:
    simulation, summary = model["simulation"], model["summary"]
    lines = [
        "Studio simulation preview: derived, non-executing output",
        f"simulation: {simulation['id']}",
        f"authority: {simulation['authority']}",
        f"execution_mode: {simulation['execution_mode']}",
        f"freshness: {simulation['freshness']}",
        f"filters: {_filters_line(simulation['filters'])}",
        f"scenarios: {summary['scenario_count']}",
        f"steps: {summary['step_count']}",
        f"path_labels: {summary['path_labels']}",
        f"validation_fail: {summary['validation_fail']}",
        "scenarios:",
    ]
    for scenario in model["scenarios"]:
        tags = ",".join(scenario["tags"]) if scenario["tags"] else "none"
        lines.append(
            f"- {scenario['id']} intent={scenario['intent']} outcome={scenario['outcome']} tags={tags} steps={len(scenario['steps'])}"
        )
        lines.append(f"    {scenario['description']}")
        for step in scenario["steps"]:
            blockers = f" blockers={len(step['blockers'])}" if step["blockers"] else ""
            exit_note = f" exit={step['exit_criteria']}" if step.get("exit_criteria") else ""
            lines.append(
                f"  {step['order']:02d}. [{step['path_label']}/{step['kind']}] {step['ref']} -> next={step['next_agent_recommendation']}{blockers}{exit_note}"
            )
            lines.append(f"      {step['summary']}")
    lines.append(f"lifecycle_map: {len(model['lifecycle_map'])} transitions")
    return "\n".join(lines) + "\n"


def _build_scenario(
    scenario_id: str,
    compiled: CompilerResult,
    transitions: dict[str, dict[str, Any]],
    validation_fail: int,
) -> dict[str, Any]:
    blueprint = _SCENARIO_BLUEPRINTS[scenario_id]
    steps = [_materialize_step(spec, transitions, validation_fail) for spec in blueprint["steps"]]
    workflow_refs = _source_refs(_dict(compiled.workflow_ir.get("workflow")).get("source_refs"))
    return {
        "id": f"simulation.scenario.{scenario_id}",
        "name": blueprint["name"],
        "intent": blueprint["intent"],
        "description": blueprint["description"],
        "tags": list(blueprint["tags"]),
        "outcome": blueprint["outcome"],
        "evidence_expectations": list(blueprint["evidence_expectations"]),
        "source_refs": _unique_source_refs([*_path_refs(blueprint["lifecycle_refs"]), *workflow_refs]),
        "steps": steps,
    }


def _materialize_step(spec: dict[str, Any], transitions: dict[str, dict[str, Any]], validation_fail: int) -> dict[str, Any]:
    transition_ref = spec.get("transition_ref")
    transition = transitions.get(transition_ref, {}) if transition_ref else {}
    path_label = spec["path_label"]
    if spec.get("block_on_validation_fail") and validation_fail > 0:
        path_label = "blocked"
    agent_ref = transition.get("agent_ref") or spec.get("agent_ref")
    next_agent = _agent_slug(agent_ref) or spec.get("next_agent_recommendation", "none")
    blockers = list(spec.get("blockers", ()))
    if path_label == "blocked" and spec.get("blocker_template"):
        blockers.append(spec["blocker_template"])
    return {
        "id": spec["id"],
        "order": spec["order"],
        "kind": spec["kind"],
        "ref": spec["ref"],
        "stage_ref": spec.get("stage_ref"),
        "transition_ref": transition_ref,
        "path_label": path_label,
        "gate": spec.get("gate"),
        "handoff": {
            "previous_agent": spec.get("previous_agent"),
            "next_agent_recommendation": next_agent,
            "handoff_ref": ".sdlc/memory/orchestrator-handoff.md",
        },
        "validation": {
            "derived_status": "fail" if path_label == "blocked" and spec.get("validation_blocked") else spec.get("validation_status", "pass"),
            "inspection_derived": True,
        },
        "blockers": blockers,
        "exit_criteria": spec.get("exit_criteria"),
        "next_agent_recommendation": next_agent,
        "summary": _trim(spec["summary"], 240),
        "lifecycle_source": spec["lifecycle_source"],
        "source_refs": _unique_source_refs(
            _source_refs(transition.get("source_refs"))
            or [{"ref_type": "path", "ref": spec["lifecycle_source"]}]
        ),
    }


def _build_lifecycle_map(transitions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for transition_id in sorted(transitions):
        transition = transitions[transition_id]
        entries.append(
            {
                "id": f"simulation.lifecycle_map.{transition_id.removeprefix('transition.')}",
                "transition_ref": transition_id,
                "from_stage": transition.get("from"),
                "to_stage": transition.get("to"),
                "lifecycle_source": TRANSITION_LIFECYCLE_SOURCES.get(transition_id, ".sdlc/process/master-workflow.md"),
                "agent_ref": transition.get("agent_ref"),
                "path_label": "expected",
                "source_refs": _unique_source_refs(_source_refs(transition.get("source_refs"))),
            }
        )
    return entries


def _validated_filters(
    *,
    scenario: str | None,
    intent: str | None,
    path_label: str | None,
    step_kind: str | None,
    tag: str | None,
) -> dict[str, str | None]:
    if scenario is not None and scenario not in VALID_SCENARIOS:
        raise SimulationPreviewInputError(f"invalid scenario: {scenario}")
    if intent is not None and intent not in VALID_INTENTS:
        raise SimulationPreviewInputError(f"invalid intent: {intent}")
    if path_label is not None and path_label not in VALID_PATH_LABELS:
        raise SimulationPreviewInputError(f"invalid path_label: {path_label}")
    if step_kind is not None and step_kind not in VALID_STEP_KINDS:
        raise SimulationPreviewInputError(f"invalid step_kind: {step_kind}")
    if tag is not None and tag not in VALID_TAGS:
        raise SimulationPreviewInputError(f"invalid tag: {tag}")
    return {
        "scenario": scenario,
        "intent": intent,
        "path_label": path_label,
        "step_kind": step_kind,
        "tag": tag,
    }


def _apply_scenario_filters(
    scenarios: tuple[dict[str, Any], ...],
    filters: dict[str, str | None],
) -> tuple[dict[str, Any], ...]:
    visible = scenarios
    if filters["scenario"] is not None:
        visible = tuple(item for item in visible if item["id"] == f"simulation.scenario.{filters['scenario']}")
    if filters["intent"] is not None:
        visible = tuple(item for item in visible if item["intent"] == filters["intent"])
    if filters["tag"] is not None:
        visible = tuple(item for item in visible if filters["tag"] in item["tags"])
    if filters["path_label"] is None and filters["step_kind"] is None:
        return visible
    filtered: list[dict[str, Any]] = []
    for scenario in visible:
        steps = [
            step
            for step in scenario["steps"]
            if (filters["path_label"] is None or step["path_label"] == filters["path_label"])
            and (filters["step_kind"] is None or step["kind"] == filters["step_kind"])
        ]
        if steps:
            filtered.append({**scenario, "steps": steps})
    return tuple(filtered)


def _filters_line(filters: dict[str, str | None]) -> str:
    active = [f"{key}={value}" for key, value in filters.items() if value is not None]
    return ", ".join(active) if active else "none"


def _path_label_counts(scenarios: tuple[dict[str, Any], ...]) -> dict[str, int]:
    counts = {label: 0 for label in VALID_PATH_LABELS}
    for scenario in scenarios:
        for step in scenario["steps"]:
            counts[step["path_label"]] = counts.get(step["path_label"], 0) + 1
    return counts


def _transition_index(compiled: CompilerResult) -> dict[str, dict[str, Any]]:
    workflow = _dict(compiled.workflow_ir.get("workflow"))
    return {str(item.get("id", "")): item for item in _items(workflow.get("transitions")) if item.get("id")}


def _agent_slug(agent_ref: Any) -> str | None:
    if not agent_ref:
        return None
    value = str(agent_ref)
    if value.startswith("cursor.agent."):
        return value.removeprefix("cursor.agent.")
    return value


def _step(
    *,
    sid: str,
    order: int,
    kind: str,
    ref: str,
    path_label: str,
    summary: str,
    lifecycle_source: str,
    stage_ref: str | None = None,
    transition_ref: str | None = None,
    agent_ref: str | None = None,
    next_agent_recommendation: str = "none",
    previous_agent: str | None = None,
    gate: dict[str, str] | None = None,
    validation_status: str = "pass",
    validation_blocked: bool = False,
    block_on_validation_fail: bool = False,
    blockers: tuple[str, ...] = (),
    blocker_template: str | None = None,
    exit_criteria: str | None = None,
) -> dict[str, Any]:
    return {
        "id": sid,
        "order": order,
        "kind": kind,
        "ref": ref,
        "stage_ref": stage_ref,
        "transition_ref": transition_ref,
        "path_label": path_label,
        "agent_ref": agent_ref,
        "next_agent_recommendation": next_agent_recommendation,
        "previous_agent": previous_agent,
        "gate": gate,
        "summary": summary,
        "lifecycle_source": lifecycle_source,
        "validation_status": validation_status,
        "validation_blocked": validation_blocked,
        "block_on_validation_fail": block_on_validation_fail,
        "blockers": blockers,
        "blocker_template": blocker_template,
        "exit_criteria": exit_criteria,
    }


_SCENARIO_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "docs_only": {
        "name": "Docs-only change",
        "intent": "DOCS_ONLY",
        "description": "SDLC_META or DOCS_ONLY scope skips app/ gates and full architecture while keeping Plane and review.",
        "tags": ("docs_scope", "happy_path"),
        "outcome": "docs_pr_merged",
        "evidence_expectations": ("Plane card on docs scope", "PR review without app/ gate"),
        "lifecycle_refs": (".sdlc/process/master-workflow.md",),
        "steps": (
            _step(sid="simulation.step.docs_only.01", order=1, kind="handoff", ref="intent.docs_only", path_label="expected", summary="Intent Analyst classifies DOCS_ONLY; Plane card on docs scope.", lifecycle_source=".sdlc/process/master-workflow.md", previous_agent="orchestrator", next_agent_recommendation="planner", exit_criteria="intent=DOCS_ONLY on Plane card"),
            _step(sid="simulation.step.docs_only.02", order=2, kind="stage", ref="stage.ticket", stage_ref="stage.ticket", path_label="expected", summary="Planner creates or updates Plane card; branch prefix docs/.", lifecycle_source=".sdlc/process/change-lifecycle.md", next_agent_recommendation="planner", gate={"label": "planning", "paths": ".sdlc/, .cursor/, docs/"}, exit_criteria="branch docs/ or SDLC paths only"),
            _step(sid="simulation.step.docs_only.03", order=3, kind="transition", ref="transition.requirements_to_architecture", transition_ref="transition.requirements_to_architecture", path_label="unsupported", summary="Full architecture transition not required for docs-only scope.", lifecycle_source=".sdlc/workflows/transitions.yaml#requirements_to_architecture"),
            _step(sid="simulation.step.docs_only.04", order=4, kind="stage", ref="stage.review", stage_ref="stage.review", path_label="expected", summary="Docs PR reviewed; no app/ implementation gate.", lifecycle_source=".sdlc/process/change-lifecycle.md", next_agent_recommendation="reviewer", exit_criteria="Reviewer APPROVE on docs diff"),
            _step(sid="simulation.step.docs_only.05", order=5, kind="transition", ref="transition.review_to_deployment", transition_ref="transition.review_to_deployment", path_label="expected", summary="Merge docs PR to develop after review approval.", lifecycle_source=".sdlc/workflows/transitions.yaml#review_to_deployment", next_agent_recommendation="devops", exit_criteria="merge to develop"),
        ),
    },
    "feature_implementation": {
        "name": "Feature implementation",
        "intent": "FEATURE",
        "description": "Standard child-card pipeline from workflow start through DevOps merge with all transitions expected.",
        "tags": ("happy_path",),
        "outcome": "feature_merged",
        "evidence_expectations": ("QA test evidence on Plane", "Reviewer APPROVE", "green CI"),
        "lifecycle_refs": (".sdlc/process/change-lifecycle.md", ".sdlc/process/master-workflow.md"),
        "steps": (
            _step(sid="simulation.step.feature.01", order=1, kind="handoff", ref="workflow.start", path_label="expected", summary="workflow start on child card opens implementation gate and branch.", lifecycle_source=".sdlc/process/change-lifecycle.md", previous_agent="orchestrator", next_agent_recommendation="implementer", gate={"label": "implementation", "paths": "app/, pyproject.toml"}, exit_criteria="feature branch checked out"),
            _step(sid="simulation.step.feature.02", order=2, kind="transition", ref="transition.architecture_to_implementation", transition_ref="transition.architecture_to_implementation", path_label="expected", summary="Architecture approved; Implementer commits on feature branch.", lifecycle_source=".sdlc/workflows/transitions.yaml#architecture_to_implementation"),
            _step(sid="simulation.step.feature.03", order=3, kind="transition", ref="transition.implementation_to_validation", transition_ref="transition.implementation_to_validation", path_label="expected", summary="Implementation complete; QA runs real tests and doctor.", lifecycle_source=".sdlc/workflows/transitions.yaml#implementation_to_validation", exit_criteria="implementer handoff Next agent=qa"),
            _step(sid="simulation.step.feature.04", order=4, kind="transition", ref="transition.validation_to_review", transition_ref="transition.validation_to_review", path_label="expected", summary="QA pass; Reviewer prepares PR review.", lifecycle_source=".sdlc/workflows/transitions.yaml#validation_to_review", exit_criteria="QA pass evidence"),
            _step(sid="simulation.step.feature.05", order=5, kind="transition", ref="transition.review_to_deployment", transition_ref="transition.review_to_deployment", path_label="expected", summary="Reviewer APPROVE; DevOps opens PR and merge path.", lifecycle_source=".sdlc/workflows/transitions.yaml#review_to_deployment", exit_criteria="Reviewer APPROVE"),
        ),
    },
    "qa_failure": {
        "name": "QA failure and AutoFixer loop",
        "intent": "FEATURE",
        "description": "Validation stage blocks review until tests pass; AutoFixer may retry twice before human escalation.",
        "tags": ("failure_path", "gate_blocked"),
        "outcome": "blocked_or_autofix_then_pass",
        "evidence_expectations": ("failing test output in QA handoff", "AutoFixer cycle count on Plane"),
        "lifecycle_refs": (".sdlc/process/master-workflow.md",),
        "steps": (
            _step(sid="simulation.step.qa_fail.01", order=1, kind="transition", ref="transition.implementation_to_validation", transition_ref="transition.implementation_to_validation", path_label="expected", summary="Implementer hands off to QA for validation.", lifecycle_source=".sdlc/workflows/transitions.yaml#implementation_to_validation"),
            _step(sid="simulation.step.qa_fail.02", order=2, kind="stage", ref="stage.validation", stage_ref="stage.validation", path_label="blocked", summary="QA reports failing tests; transition to review blocked.", lifecycle_source=".sdlc/process/master-workflow.md", validation_status="fail", validation_blocked=True, next_agent_recommendation="autofixer", blockers=("QA_FAIL",), blocker_template="validation_failures_present", exit_criteria="all tests pass"),
            _step(sid="simulation.step.qa_fail.03", order=3, kind="handoff", ref="autofix.loop", path_label="expected", summary="AutoFixer attempts fix; re-QA up to two cycles.", lifecycle_source=".sdlc/process/master-workflow.md", previous_agent="qa", next_agent_recommendation="autofixer", exit_criteria="<=2 AutoFixer cycles"),
            _step(sid="simulation.step.qa_fail.04", order=4, kind="transition", ref="transition.validation_to_review", transition_ref="transition.validation_to_review", path_label="blocked", summary="validation_to_review remains blocked until QA pass.", lifecycle_source=".sdlc/workflows/transitions.yaml#validation_to_review", block_on_validation_fail=True, validation_blocked=True, blocker_template="qa_not_passed"),
            _step(sid="simulation.step.qa_fail.05", order=5, kind="handoff", ref="human.escalation", path_label="unsupported", summary="After two AutoFixer cycles, orchestrator stops and asks human.", lifecycle_source=".sdlc/process/master-workflow.md", next_agent_recommendation="human"),
        ),
    },
    "reviewer_escalation": {
        "name": "Reviewer escalation",
        "intent": "FEATURE",
        "description": "Reviewer ESCALATE blocks merge and finish-change until a human resolves the finding.",
        "tags": ("failure_path", "gate_blocked", "human_escalation"),
        "outcome": "blocked_until_human",
        "evidence_expectations": ("Reviewer ESCALATE note on PR", "human decision on Plane"),
        "lifecycle_refs": (".sdlc/process/master-workflow.md",),
        "steps": (
            _step(sid="simulation.step.review_esc.01", order=1, kind="transition", ref="transition.validation_to_review", transition_ref="transition.validation_to_review", path_label="expected", summary="QA pass enables PR and review stage.", lifecycle_source=".sdlc/workflows/transitions.yaml#validation_to_review"),
            _step(sid="simulation.step.review_esc.02", order=2, kind="stage", ref="stage.review", stage_ref="stage.review", path_label="blocked", summary="Reviewer ESCALATE; merge and finish-change blocked.", lifecycle_source=".sdlc/process/master-workflow.md", next_agent_recommendation="human", blockers=("REVIEW_ESCALATE",), blocker_template="reviewer_escalate", exit_criteria="Reviewer APPROVE or human override"),
            _step(sid="simulation.step.review_esc.03", order=3, kind="transition", ref="transition.review_to_deployment", transition_ref="transition.review_to_deployment", path_label="blocked", summary="review_to_deployment blocked until APPROVE.", lifecycle_source=".sdlc/workflows/transitions.yaml#review_to_deployment", blocker_template="review_not_approved"),
        ),
    },
    "devops_finish": {
        "name": "DevOps finish",
        "intent": "FEATURE",
        "description": "Post-APPROVE merge path through finish-change and observability checklist.",
        "tags": ("happy_path", "finish_flow"),
        "outcome": "card_done_merged",
        "evidence_expectations": ("PR merged to develop", "Plane card Done", "workflow finish gate closed"),
        "lifecycle_refs": (".sdlc/process/change-lifecycle.md",),
        "steps": (
            _step(sid="simulation.step.devops.01", order=1, kind="stage", ref="stage.review", stage_ref="stage.review", path_label="expected", summary="Reviewer APPROVE with green CI prerequisite.", lifecycle_source=".sdlc/process/master-workflow.md", next_agent_recommendation="devops", exit_criteria="Reviewer APPROVE and green CI"),
            _step(sid="simulation.step.devops.02", order=2, kind="transition", ref="transition.review_to_deployment", transition_ref="transition.review_to_deployment", path_label="expected", summary="DevOps pushes PR and runs finish-change merge flow.", lifecycle_source=".sdlc/workflows/transitions.yaml#review_to_deployment"),
            _step(sid="simulation.step.devops.03", order=3, kind="handoff", ref="workflow.finish", path_label="expected", summary="auto_merge_pr closes gate; Plane card marked Done.", lifecycle_source=".sdlc/process/change-lifecycle.md", previous_agent="devops", next_agent_recommendation="observer", exit_criteria="Plane card Done"),
            _step(sid="simulation.step.devops.04", order=4, kind="transition", ref="transition.deployment_to_observability", transition_ref="transition.deployment_to_observability", path_label="expected", summary="Observability checklist after deployment.", lifecycle_source=".sdlc/workflows/transitions.yaml#deployment_to_observability"),
            _step(sid="simulation.step.devops.05", order=5, kind="transition", ref="transition.incident_to_autofix", transition_ref="transition.incident_to_autofix", path_label="unsupported", summary="Incident autofix path not part of standard finish flow.", lifecycle_source=".sdlc/workflows/transitions.yaml#incident_to_autofix"),
        ),
    },
}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
