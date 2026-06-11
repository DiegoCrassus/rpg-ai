"""S5 registry and validation projections over Foundation ``studio/``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from studio.engine.compiler_core import CompilerInputError, compile_studio_sources
from studio.engine.mvp_test_skeleton import build_mvp_test_skeleton
from studio.engine.publish_evidence import (
    PublishEvidenceInputError,
    build_publish_evidence_from_sources,
)
from studio.engine.simulation_preview import (
    SimulationPreviewInputError,
    build_simulation_preview_from_sources,
)
from studio.engine.validation_inspection import (
    ValidationInspectionInputError,
    build_validation_inspection_from_sources,
)
from studio.engine.validator_core import validate_studio_sources
from studio.engine.workflow_assistance import (
    WorkflowAssistanceInputError,
    build_workflow_assistance_from_sources,
)
from studio_service.api.errors import StudioApiError
from studio_service.services.doctor_runner import run_doctor_in_workspace
from studio_service.services.engine import _compiler_input_error


def _section_items(report: dict[str, Any], section_id: str) -> list[dict[str, str]]:
    for section in report.get("sections") or []:
        if section.get("id") == section_id:
            items = section.get("items") or []
            return [
                {"id": str(item.get("label", "")), "detail": str(item.get("value", ""))}
                for item in items
                if item.get("label")
            ]
    return []


def build_registry_graph(root: Path) -> dict[str, Any]:
    """Registry entity graph plus broken-ref projection from compile report."""

    try:
        compiled = compile_studio_sources(root)
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc

    graph_ir = compiled.graph_ir
    report = compiled.report
    counts = (report.get("summary") or {}).get("counts") or {}
    unresolved = _section_items(report, "unresolved_relationships")
    missing_paths = _section_items(report, "missing_optional_source_paths")

    return {
        "graph": graph_ir.get("graph"),
        "nodes": graph_ir.get("nodes") or [],
        "edges": graph_ir.get("edges") or [],
        "broken_refs": {
            "unresolved_relationships": unresolved,
            "missing_optional_source_paths": missing_paths,
        },
        "summary": {
            "status": report.get("status"),
            "counts": counts,
            "broken_ref_count": len(unresolved) + len(missing_paths),
        },
    }


def build_validation_inspection(
    root: Path,
    *,
    status: str | None = None,
    check_type: str | None = None,
    target_type: str | None = None,
    group_by: str = "status",
) -> dict[str, Any]:
    try:
        return build_validation_inspection_from_sources(
            root,
            status=status,
            check_type=check_type,
            target_type=target_type,
            group_by=group_by,
        )
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc
    except ValidationInspectionInputError as exc:
        raise StudioApiError(400, "INVALID_VALIDATION_FILTER", str(exc)) from exc


def run_validation(root: Path) -> dict[str, Any]:
    try:
        result = validate_studio_sources(root)
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc
    return {
        "report": result.report,
        "results": result.results,
        "summary": result.summary,
    }


def run_repo_doctor(root: Path) -> dict[str, Any]:
    exit_code, summary, details = run_doctor_in_workspace(root, root)
    return {
        "exit_code": exit_code,
        "summary": summary,
        "details": details,
    }


def build_simulation_preview(
    root: Path,
    *,
    scenario: str | None = None,
    intent: str | None = None,
    path_label: str | None = None,
    step_kind: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    try:
        return build_simulation_preview_from_sources(
            root,
            scenario=scenario,
            intent=intent,
            path_label=path_label,
            step_kind=step_kind,
            tag=tag,
        )
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc
    except SimulationPreviewInputError as exc:
        raise StudioApiError(400, "INVALID_SIMULATION_FILTER", str(exc)) from exc


def build_workflow_assistance(root: Path, *, kind: str | None = None) -> dict[str, Any]:
    try:
        return build_workflow_assistance_from_sources(root, kind=kind)
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc
    except WorkflowAssistanceInputError as exc:
        raise StudioApiError(400, "INVALID_ASSISTANCE_FILTER", str(exc)) from exc


def list_test_skeleton() -> dict[str, Any]:
    return build_mvp_test_skeleton()


def build_evidence_draft(
    root: Path,
    *,
    card: str | None = None,
    title: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    try:
        return build_publish_evidence_from_sources(
            root,
            card=card,
            title=title,
            branch=branch,
        )
    except CompilerInputError as exc:
        raise _compiler_input_error(exc) from exc
    except PublishEvidenceInputError as exc:
        raise StudioApiError(400, "INVALID_EVIDENCE_FILTER", str(exc)) from exc
