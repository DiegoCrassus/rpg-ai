"""Deterministic, in-memory Studio validator core."""

from __future__ import annotations

import posixpath
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from studio.engine.compiler_core import CompilerResult, compile_studio_sources
from studio.engine.reporting import build_report

_ALLOWED_PATH_PREFIXES = (".sdlc/", ".cursor/", "studio/", "docs/")
_FORBIDDEN_PATH_PREFIXES = ("app/", "studio/engine/examples/", "studio/engine/generated/", "specs/")
_FORBIDDEN_PATH_PARTS = (
    "local tickets", "local backlog", "local evidence", "generated snapshots",
    "generated reports", "command outputs", "ci logs",
)
_CHECKER_SOURCE = {"ref_type": "path", "ref": "studio/engine/validator_core.py"}
_CHECKER_AUTHORITY = {"ref_type": "path", "ref": "studio/docs/contracts/validation-result-ir-contract.md"}
_CHECKER_METADATA = {
    "checked_by": "studio.engine.validator_core",
    "checker_version": "0.1.0",
    "checker_authority": _CHECKER_AUTHORITY,
}
_VALIDATOR_SOURCE_REFS = (
    {"ref_type": "path", "ref": "studio/engine/validator_core.py"},
    {"ref_type": "path", "ref": "studio/engine/schemas/validation-result.schema.yaml"},
)


@dataclass(frozen=True)
class ValidationRunResult:
    """In-memory validation records and a deterministic status summary."""

    results: tuple[dict[str, Any], ...]
    summary: dict[str, int]
    report: dict[str, Any] = field(default_factory=dict)


def validate_studio_sources(root: Path | str) -> ValidationRunResult:
    """Compile Studio sources and validate the in-memory compiler result."""

    return validate_compiler_result(compile_studio_sources(root), root)


def validate_compiler_result(result: CompilerResult, root: Path | str) -> ValidationRunResult:
    """Validate a Studio compiler result without writing files or invoking tools."""

    repo_root = Path(root)
    records = (
        _validate_graph_relationship_targets(result.graph_ir),
        _validate_workflow_transition_targets(result.workflow_ir),
        _validate_graph_source_refs(result.graph_ir, repo_root),
        _validate_workflow_source_refs(result.workflow_ir, repo_root),
        _validate_output_boundaries(result),
        _validate_authority_boundaries(result),
    )
    summary = _summary(records)
    return ValidationRunResult(results=records, summary=summary, report=_build_validation_report(records, summary))


def _validate_graph_relationship_targets(graph_ir: dict[str, Any]) -> dict[str, Any]:
    graph = graph_ir.get("graph") if isinstance(graph_ir.get("graph"), dict) else {}
    node_ids = {str(node.get("id", "")) for node in _dict_items(graph_ir.get("nodes"))}
    failures: list[str] = []
    source_refs: list[dict[str, str]] = []
    for edge in _dict_items(graph_ir.get("edges")):
        edge_id = str(edge.get("id", "edge.unknown"))
        source_refs.extend(_source_refs(edge.get("source_refs")))
        for field_name in ("from", "to"):
            target = str(edge.get(field_name, ""))
            if target not in node_ids:
                failures.append(f"{edge_id}.{field_name} references missing node {target or '<empty>'}.")
    if failures:
        return _result(
            "validation.graph.relationship_targets",
            target_ref={"ref_type": "graph", "ref": str(graph.get("id", "graph.unknown"))},
            check_type="relationship_target",
            status="fail",
            messages=[_message("error", text) for text in sorted(failures)],
            source_refs=[*source_refs, *_VALIDATOR_SOURCE_REFS],
        )
    return _result(
        "validation.graph.relationship_targets",
        target_ref={"ref_type": "graph", "ref": str(graph.get("id", "graph.unknown"))},
        check_type="relationship_target",
        status="pass",
        messages=[_message("info", "All graph edge endpoints reference existing nodes.")],
        source_refs=[*_source_refs(graph.get("source_refs")), *_VALIDATOR_SOURCE_REFS],
    )


def _validate_workflow_transition_targets(workflow_ir: dict[str, Any]) -> dict[str, Any]:
    workflow = workflow_ir.get("workflow") if isinstance(workflow_ir.get("workflow"), dict) else {}
    stage_ids = {str(stage.get("id", "")) for stage in _dict_items(workflow.get("stages"))}
    failures: list[str] = []
    source_refs: list[dict[str, str]] = []
    for transition in _dict_items(workflow.get("transitions")):
        transition_id = str(transition.get("id", "transition.unknown"))
        source_refs.extend(_source_refs(transition.get("source_refs")))
        for field_name in ("from", "to"):
            target = str(transition.get(field_name, ""))
            if target not in stage_ids:
                failures.append(f"{transition_id}.{field_name} references missing stage {target or '<empty>'}.")
    if failures:
        return _result(
            "validation.workflow.transition_targets",
            target_ref={"ref_type": "workflow", "ref": str(workflow.get("id", "workflow.unknown"))},
            check_type="relationship_target",
            status="fail",
            messages=[_message("error", text) for text in sorted(failures)],
            source_refs=[*source_refs, *_VALIDATOR_SOURCE_REFS],
        )
    return _result(
        "validation.workflow.transition_targets",
        target_ref={"ref_type": "workflow", "ref": str(workflow.get("id", "workflow.unknown"))},
        check_type="relationship_target",
        status="pass",
        messages=[_message("info", "All workflow transitions reference existing stages.")],
        source_refs=[*_source_refs(workflow.get("source_refs")), *_VALIDATOR_SOURCE_REFS],
    )


def _validate_graph_source_refs(graph_ir: dict[str, Any], root: Path) -> dict[str, Any]:
    graph = graph_ir.get("graph") if isinstance(graph_ir.get("graph"), dict) else {}
    refs: list[dict[str, str]] = []
    refs.extend(_source_refs(graph.get("source_refs")))
    for node in _dict_items(graph_ir.get("nodes")):
        refs.extend(_source_refs(node.get("source_refs")))
    for edge in _dict_items(graph_ir.get("edges")):
        refs.extend(_source_refs(edge.get("source_refs")))
    return _validate_source_ref_set(
        "validation.graph.source_refs",
        target_ref={"ref_type": "graph", "ref": str(graph.get("id", "graph.unknown"))},
        root=root,
        refs=refs,
        pass_text="All graph source refs exist within allowed scopes.",
    )


def _validate_workflow_source_refs(workflow_ir: dict[str, Any], root: Path) -> dict[str, Any]:
    workflow = workflow_ir.get("workflow") if isinstance(workflow_ir.get("workflow"), dict) else {}
    refs: list[dict[str, str]] = []
    refs.extend(_source_refs(workflow.get("source_refs")))
    for stage in _dict_items(workflow.get("stages")):
        refs.extend(_source_refs(stage.get("source_refs")))
    for transition in _dict_items(workflow.get("transitions")):
        refs.extend(_source_refs(transition.get("source_refs")))
    return _validate_source_ref_set(
        "validation.workflow.source_refs",
        target_ref={"ref_type": "workflow", "ref": str(workflow.get("id", "workflow.unknown"))},
        root=root,
        refs=refs,
        pass_text="All workflow source refs exist within allowed scopes.",
    )


def _validate_source_ref_set(
    result_id: str,
    *,
    target_ref: dict[str, str],
    root: Path,
    refs: list[dict[str, str]],
    pass_text: str,
) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    for ref in _unique_source_refs(refs):
        if ref.get("ref_type") != "path":
            continue
        path = ref["ref"]
        if not _path_allowed(path):
            failures.append(_message("error", f"Source ref is outside allowed scopes: {path}.", path=path))
        elif not (root / path).exists():
            failures.append(_message("error", f"Source ref path does not exist: {path}.", path=path))
    if failures:
        return _result(
            result_id,
            target_ref=target_ref,
            check_type="path_scope",
            status="fail",
            messages=failures,
            source_refs=_VALIDATOR_SOURCE_REFS,
        )
    return _result(
        result_id,
        target_ref=target_ref,
        check_type="path_exists",
        status="pass",
        messages=[_message("info", pass_text)],
        source_refs=[*_unique_source_refs(refs), *_VALIDATOR_SOURCE_REFS],
    )


def _validate_output_boundaries(result: CompilerResult) -> dict[str, Any]:
    refs = _compiler_source_refs(result)
    forbidden = sorted(ref["ref"] for ref in refs if ref.get("ref_type") == "path" and _path_forbidden(ref["ref"]))
    if forbidden:
        return _result(
            "validation.compiler.output_boundaries",
            target_ref={"ref_type": "path", "ref": "studio"},
            check_type="policy",
            status="fail",
            messages=[_message("error", f"Compiler result references forbidden generated output path: {path}.", path=path) for path in forbidden],
            source_refs=_VALIDATOR_SOURCE_REFS,
        )
    return _result(
        "validation.compiler.output_boundaries",
        target_ref={"ref_type": "path", "ref": "studio"},
        check_type="policy",
        status="pass",
        messages=[_message("info", "Compiler validation uses in-memory inputs and no persisted generated output locations.")],
        source_refs=[_CHECKER_SOURCE, {"ref_type": "path", "ref": "studio/docs/contracts/compiler-validator-boundaries.md"}],
    )


def _validate_authority_boundaries(result: CompilerResult) -> dict[str, Any]:
    authority = result.report.get("authority") if isinstance(result.report, dict) else None
    if authority != "derived_non_authoritative":
        return _result(
            "validation.compiler.authority_boundaries",
            target_ref={"ref_type": "path", "ref": "studio/engine/compiler_core.py"},
            check_type="policy",
            status="fail",
            messages=[_message("error", "Compiler report authority must remain derived_non_authoritative.")],
            source_refs=[_CHECKER_SOURCE, {"ref_type": "path", "ref": "studio/docs/contracts/compiler-validator-boundaries.md"}],
        )
    return _result(
        "validation.compiler.authority_boundaries",
        target_ref={"ref_type": "path", "ref": "studio/engine/compiler_core.py"},
        check_type="policy",
        status="pass",
        messages=[_message("info", "Compiler report authority remains derived and non-authoritative.")],
        source_refs=[_CHECKER_SOURCE, {"ref_type": "path", "ref": "studio/docs/contracts/compiler-validator-boundaries.md"}],
    )


def _compiler_source_refs(result: CompilerResult) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    refs.extend(_source_refs(result.graph_ir.get("graph", {}).get("source_refs")))
    for node in _dict_items(result.graph_ir.get("nodes")):
        refs.extend(_source_refs(node.get("source_refs")))
    for edge in _dict_items(result.graph_ir.get("edges")):
        refs.extend(_source_refs(edge.get("source_refs")))
    workflow = result.workflow_ir.get("workflow", {})
    refs.extend(_source_refs(workflow.get("source_refs")))
    for stage in _dict_items(workflow.get("stages")):
        refs.extend(_source_refs(stage.get("source_refs")))
    for transition in _dict_items(workflow.get("transitions")):
        refs.extend(_source_refs(transition.get("source_refs")))
    refs.extend(_source_refs(result.report.get("source_refs") if isinstance(result.report, dict) else None))
    return _unique_source_refs(refs)


def _build_validation_report(records: tuple[dict[str, Any], ...], summary: dict[str, int]) -> dict[str, Any]:
    status = _report_status(summary)
    return build_report(
        report_id="report.studio.validate",
        kind="validate",
        status=status,
        summary={"description": "Validated derived Studio compiler outputs in memory.", "counts": summary},
        sections=[
            {
                "id": "findings",
                "title": "Findings",
                "status": status,
                "items": [{"label": str(record.get("id", "unknown")), "status": str(record.get("status", "not_run"))} for record in records],
            },
            {
                "id": "boundaries",
                "title": "Boundaries",
                "status": "pass",
                "items": [
                    {"label": "persistence", "value": "stdout_only"},
                    {"label": "authority", "value": "Plane and GitHub remain durable evidence authorities"},
                ],
            },
        ],
        source_refs=[*_VALIDATOR_SOURCE_REFS, {"ref_type": "path", "ref": "studio/docs/contracts/compiler-validator-boundaries.md"}],
        non_goals=[
            "No workflow, command, gate, CI, lint, or doctor execution.",
            "No copied source bodies, command outputs, CI logs, local evidence, or durable delivery evidence.",
            "No replacement behavior for .sdlc/, .cursor/, Plane, GitHub, or .sdlc/registry/.",
        ],
    )


def _report_status(summary: dict[str, int]) -> str:
    if summary.get("fail", 0):
        return "fail"
    if summary.get("warn", 0):
        return "warn"
    if summary.get("not_run", 0) and not summary.get("pass", 0):
        return "not_run"
    return "pass"


def _result(
    result_id: str,
    *,
    target_ref: dict[str, str],
    check_type: str,
    status: str,
    messages: list[dict[str, str]],
    source_refs: list[dict[str, str]] | tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "id": result_id,
        "target_ref": target_ref,
        "check_type": check_type,
        "status": status,
        "messages": messages,
        "source_refs": _unique_source_refs(source_refs),
        **_CHECKER_METADATA,
    }


def _message(level: str, text: str, *, path: str | None = None) -> dict[str, str]:
    message = {"level": level, "text": text}
    if path:
        message["path"] = path
    return message


def _source_refs(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    refs: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, str) and item:
            refs.append({"ref_type": "path", "ref": item})
        elif isinstance(item, dict):
            ref_type = str(item.get("ref_type", "path"))
            ref = str(item.get("ref", ""))
            if ref:
                normalized = {"ref_type": ref_type, "ref": ref}
                summary = item.get("summary")
                if isinstance(summary, str) and summary:
                    normalized["summary"] = summary
                refs.append(normalized)
    return refs


def _unique_source_refs(refs: list[dict[str, str]] | tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for ref in refs:
        key = (ref["ref_type"], ref["ref"])
        unique.setdefault(key, ref)
    return [unique[key] for key in sorted(unique)]


def _dict_items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _path_allowed(path: str) -> bool:
    normalized = _normalize_repo_relative_path(path)
    return normalized is not None and normalized.startswith(_ALLOWED_PATH_PREFIXES) and not _path_forbidden(normalized)


def _path_forbidden(path: str) -> bool:
    normalized = _normalize_repo_relative_path(path)
    lowered = path.lower()
    return normalized is None or normalized.startswith(_FORBIDDEN_PATH_PREFIXES) or any(part in lowered for part in _FORBIDDEN_PATH_PARTS)


def _normalize_repo_relative_path(path: str) -> str | None:
    normalized = posixpath.normpath(path.replace("\\", "/")) if path else "."
    if normalized in (".", "..") or normalized.startswith(("../", "/", "\\")):
        return None
    return normalized


def _summary(records: tuple[dict[str, Any], ...]) -> dict[str, int]:
    statuses = ("pass", "warn", "fail", "not_run")
    return {status: sum(1 for record in records if record["status"] == status) for status in statuses}
