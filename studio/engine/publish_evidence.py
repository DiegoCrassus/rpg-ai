"""Derived, non-executing publish evidence workflow projection."""

from __future__ import annotations

import re
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

EVIDENCE_PROJECTION_ID = "evidence.sdlc_studio.projection"
EVIDENCE_TEMPLATE_REF = ".sdlc/templates/plane/evidence-template.json"
EVIDENCE_SOURCE_PATHS = (
    "studio/engine/publish_evidence.py",
    "studio/docs/prototypes/ai-publish-evidence-prototype.md",
    EVIDENCE_TEMPLATE_REF,
    "docs/roadmap/sdlc-studio-mvp-roadmap.md",
)
EVIDENCE_FIELD_KEYS = (
    "card",
    "title",
    "summary",
    "problems_solved",
    "technical",
    "validation",
    "artifacts",
    "context_for_future",
)
CARD_PATTERN = re.compile(r"^RPG-\d+$")
EVIDENCE_NON_GOALS = (
    "Does not post comments, update Plane cards, or mutate GitHub state.",
    "Does not run pytest, make sdlc-doctor, CI, or shell workflows.",
    "Does not write evidence JSON files to the repository or persist outputs.",
    "Does not present derived projection as authoritative QA or gate evidence.",
)
NOT_APPLICABLE = "not applicable — Studio does not read live GitHub or Plane state"


class PublishEvidenceInputError(ValueError):
    """Raised for unsupported publish evidence filters."""


def build_publish_evidence_from_sources(
    root: Any,
    *,
    card: str | None = None,
    title: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Compile, validate, derive inspection data, and project evidence fields in memory."""

    compiled = compile_studio_sources(root)
    validation = validate_compiler_result(compiled, root)
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    return build_publish_evidence_model(
        compiled,
        validation,
        canvas,
        inspection,
        card=card,
        title=title,
        branch=branch,
    )


def build_publish_evidence_model(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    canvas: CanvasViewModel,
    inspection: dict[str, Any],
    *,
    card: str | None = None,
    title: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic evidence-shaped projection from derived pipeline outputs."""

    resolved_card = _resolved_card(card)
    resolved_title = title or "[SDLC Studio] Derived pipeline evidence projection"
    resolved_branch = branch or NOT_APPLICABLE
    insp_summary = inspection["summary"]
    by_status = insp_summary["by_status"]
    fail_count = by_status.get("fail", 0)
    evidence_fields = _build_evidence_fields(
        compiled,
        validation,
        inspection,
        canvas,
        card=resolved_card,
        title=resolved_title,
        branch=resolved_branch,
    )
    return {
        "projection": {
            "id": EVIDENCE_PROJECTION_ID,
            "authority": AUTHORITY,
            "template_ref": EVIDENCE_TEMPLATE_REF,
            "execution_mode": "non_executing_projection",
            "source_refs": _unique_source_refs(
                [
                    *_path_refs(EVIDENCE_SOURCE_PATHS),
                    *_source_refs(compiled.report.get("source_refs")),
                    *_source_refs(validation.report.get("source_refs")),
                ]
            ),
            "non_goals": list(EVIDENCE_NON_GOALS),
            "filters": {"card": resolved_card, "title": resolved_title, "branch": resolved_branch},
        },
        "summary": {
            "template_field_count": len(EVIDENCE_FIELD_KEYS),
            "validation_total": insp_summary["total_records"],
            "validation_fail": fail_count,
            "validation_warn": by_status.get("warn", 0),
            "validation_pass": by_status.get("pass", 0),
            "problems_solved_count": len(evidence_fields["problems_solved"]),
            "context_for_future_count": len(evidence_fields["context_for_future"]),
        },
        "evidence_fields": evidence_fields,
    }


def render_publish_evidence_text(model: dict[str, Any]) -> str:
    """Render a concise stdout-only publish evidence projection summary."""

    projection = model["projection"]
    summary = model["summary"]
    fields = model["evidence_fields"]
    lines = [
        "Studio publish evidence: derived, non-authoritative output",
        f"projection: {projection['id']}",
        f"authority: {projection['authority']}",
        f"execution_mode: {projection['execution_mode']}",
        f"template: {projection['template_ref']}",
        f"card: {fields['card']}",
        f"title: {fields['title']}",
        f"summary: {fields['summary']}",
        *(f"{key.replace('_', ' ')}: {summary[key]}" for key in sorted(summary)),
        "problems_solved:",
        *(f"- {item}" for item in fields["problems_solved"]),
        "validation:",
        *(f"- {key}: {value}" for key, value in sorted(fields["validation"].items())),
        "artifacts:",
        *(f"- {key}: {value}" for key, value in sorted(fields["artifacts"].items())),
        "context_for_future:",
        *(f"- {item}" for item in fields["context_for_future"]),
        "reminder: projection is transient stdout/in-memory only; post to Plane manually after real QA/CI.",
    ]
    return "\n".join(lines) + "\n"


def _build_evidence_fields(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    inspection: dict[str, Any],
    canvas: CanvasViewModel,
    *,
    card: str,
    title: str,
    branch: str,
) -> dict[str, Any]:
    by_status = inspection["summary"]["by_status"]
    fail_count = by_status.get("fail", 0)
    warn_count = by_status.get("warn", 0)
    pass_count = by_status.get("pass", 0)
    not_run = by_status.get("not_run", 0)
    compile_status = str(compiled.report.get("status", "pass"))
    canvas_id = str(canvas.canvas.get("id", "canvas.unknown"))
    return {
        "card": card,
        "title": title,
        "summary": _trim(
            f"Deterministic evidence-field projection from Studio compile/validate pipeline "
            f"({pass_count} pass, {warn_count} warn, {fail_count} fail validation records).",
            240,
        ),
        "problems_solved": _problems_solved(compiled, inspection),
        "technical": {
            "modules": _technical_modules(compiled),
            "decisions": _technical_decisions(fail_count, compile_status),
            "files_changed": _technical_files(compiled),
        },
        "validation": {
            "tests": _trim(
                f"studio validate summary: pass={pass_count}, warn={warn_count}, "
                f"fail={fail_count}, not_run={not_run} (derived; not pytest output)",
                240,
            ),
            "doctor": "not run from Studio projection; run make sdlc-doctor separately",
            "ci": "not run from Studio projection",
        },
        "artifacts": {
            "pr": NOT_APPLICABLE,
            "branch": branch,
            "commit": NOT_APPLICABLE,
            "docs": _artifact_docs(),
        },
        "context_for_future": _context_for_future(fail_count, canvas_id),
    }


def _problems_solved(compiled: CompilerResult, inspection: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for record in inspection["records"]:
        if record["status"] not in ("fail", "warn"):
            continue
        target = record["target"]
        problems.append(
            _trim(
                f"Review {record['status']} validation {record['validation_ref']} "
                f"for {target['ref_type']}:{target['ref']}.",
                240,
            )
        )
    for section in _items(compiled.report.get("sections")):
        if str(section.get("id", "")) != "unresolved_relationships":
            continue
        for item in _items(section.get("items")):
            label = str(item.get("label", "unknown"))
            problems.append(_trim(f"Resolve unresolved compile relationship: {label}.", 240))
    if not problems:
        problems.append("No validation failures or unresolved compile relationships in derived pipeline inputs.")
    return sorted(dict.fromkeys(problems))


def _technical_modules(compiled: CompilerResult) -> list[str]:
    modules = {
        path.split("/", 1)[0] + "/" + path.split("/", 1)[1].split(".", 1)[0]
        for path in _collect_paths(compiled)
        if path.startswith("studio/") and path.endswith(".py") and path != "studio/__init__.py"
    }
    if not modules:
        modules = {"studio/engine/publish_evidence", "studio/engine/compiler_core", "studio/engine/validator_core"}
    return sorted(modules)[:12]


def _technical_decisions(fail_count: int, compile_status: str) -> list[str]:
    decisions = [
        "Evidence fields are projected deterministically from compile and validate outputs only.",
        "Plane posting remains a separate human or DevOps step outside Studio.",
    ]
    if fail_count > 0:
        decisions.append("Resolve derived validation failures before treating projection as delivery-ready.")
    if compile_status in ("warn", "fail"):
        decisions.append(f"Compile report status={compile_status}; review compile sections before publish.")
    return decisions


def _technical_files(compiled: CompilerResult) -> list[str]:
    paths = sorted(_collect_paths(compiled))
    return [path for path in paths if not path.startswith("app/")][:25]


def _artifact_docs() -> list[str]:
    return sorted(
        {
            "studio/docs/prototypes/ai-publish-evidence-prototype.md",
            "studio/README.md",
            EVIDENCE_TEMPLATE_REF,
            "docs/roadmap/sdlc-studio-mvp-roadmap.md",
        }
    )


def _context_for_future(fail_count: int, canvas_id: str) -> list[str]:
    context = [
        "Post evidence_fields to Plane manually after QA, Reviewer approval, and green CI on the feature branch.",
        f"Canvas reference for derived overlays: {canvas_id}.",
        "Do not commit evidence JSON files; Plane remains the durable evidence authority.",
    ]
    if fail_count > 0:
        context.insert(0, "Resolve derived validation failures before publishing Done evidence to Plane.")
    return context


def _collect_paths(compiled: CompilerResult) -> set[str]:
    paths: set[str] = set()
    for ref in _source_refs(compiled.report.get("source_refs")):
        if ref["ref_type"] == "path":
            paths.add(ref["ref"])
    for section in _items(compiled.report.get("sections")):
        for item in _items(section.get("items")):
            label = str(item.get("label", ""))
            if label.startswith((".sdlc/", "studio/", ".cursor/", "docs/")):
                paths.add(label)
    return paths


def _resolved_card(card: str | None) -> str:
    resolved = card or "RPG-N"
    if resolved == "RPG-N":
        return resolved
    if not CARD_PATTERN.match(resolved):
        raise PublishEvidenceInputError(f"invalid card: {resolved}")
    return resolved


def _items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
