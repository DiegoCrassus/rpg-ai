"""Shared deterministic Studio report helpers."""

from __future__ import annotations

from typing import Any

AUTHORITY = "derived_non_authoritative"
STATUSES = ("pass", "warn", "fail", "not_run")


def build_report(
    *,
    report_id: str,
    kind: str,
    status: str,
    summary: dict[str, Any],
    sections: list[dict[str, Any]],
    source_refs: list[str | dict[str, str]] | tuple[str | dict[str, str], ...],
    non_goals: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    """Build the shared report envelope without persisting or executing anything."""

    if kind not in {"compile", "validate"}:
        raise ValueError(f"Unsupported report kind: {kind}")
    if status not in STATUSES:
        raise ValueError(f"Unsupported report status: {status}")
    return {
        "id": report_id,
        "kind": kind,
        "status": status,
        "authority": AUTHORITY,
        "summary": _normalize_summary(summary),
        "sections": _normalize_sections(sections),
        "source_refs": _normalize_source_refs(source_refs),
        "non_goals": [str(item) for item in non_goals],
    }


def render_report_text(report: dict[str, Any]) -> str:
    """Render concise text from the same report envelope emitted as JSON."""

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    counts = summary.get("counts") if isinstance(summary.get("counts"), dict) else {}
    lines = [
        f"Studio {report.get('kind', 'report')}: derived, non-authoritative output",
        f"status: {report.get('status', 'unknown')}",
    ]
    description = summary.get("description")
    if isinstance(description, str) and description:
        lines.append(f"summary: {description}")
    if counts:
        lines.extend(f"{key.replace('_', ' ')}: {counts[key]}" for key in sorted(counts))
    for section in _dict_items(report.get("sections")):
        lines.append(f"{section.get('title', section.get('id', 'section'))}:")
        for item in _dict_items(section.get("items")):
            label = item.get("label", item.get("id", "item"))
            value = item.get("value", item.get("status", ""))
            lines.append(f"- {label}: {value}")
    lines.append("reminder: CLI stdout is derived and non-authoritative only.")
    return "\n".join(lines) + "\n"


def _normalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    description = summary.get("description")
    if isinstance(description, str) and description:
        normalized["description"] = description
    counts = summary.get("counts")
    if isinstance(counts, dict):
        normalized["counts"] = {str(key): value for key, value in sorted(counts.items()) if isinstance(value, int)}
    details = summary.get("details")
    if isinstance(details, list):
        normalized["details"] = [str(item) for item in details]
    return normalized


def _normalize_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for section in sections:
        section_id = str(section.get("id", "")).strip()
        if not section_id:
            continue
        record: dict[str, Any] = {
            "id": section_id,
            "title": str(section.get("title", section_id)).strip() or section_id,
            "status": str(section.get("status", "not_run")),
            "items": _normalize_items(section.get("items")),
        }
        summary = section.get("summary")
        if isinstance(summary, str) and summary:
            record["summary"] = summary
        normalized.append(record)
    return normalized


def _normalize_items(value: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in _dict_items(value):
        label = str(item.get("label", item.get("id", ""))).strip()
        if not label:
            continue
        record = {"label": label}
        if "value" in item:
            record["value"] = item["value"]
        if "status" in item:
            record["status"] = str(item["status"])
        items.append(record)
    return items


def _normalize_source_refs(
    source_refs: list[str | dict[str, str]] | tuple[str | dict[str, str], ...],
) -> list[dict[str, str]]:
    refs: dict[tuple[str, str], dict[str, str]] = {}
    for item in source_refs:
        if isinstance(item, str):
            ref_type = "path"
            ref = item
        elif isinstance(item, dict):
            ref_type = str(item.get("ref_type", "path"))
            ref = str(item.get("ref", ""))
        else:
            continue
        if ref:
            refs.setdefault((ref_type, ref), {"ref_type": ref_type, "ref": ref})
    return [refs[key] for key in sorted(refs)]


def _dict_items(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
