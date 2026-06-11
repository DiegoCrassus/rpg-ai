"""Derived, non-authoritative validation inspection view model."""

from typing import Any

from studio.engine.canvas_view_model import CanvasViewModel, build_canvas_view_model
from studio.engine.compiler_core import CompilerResult, compile_studio_sources
from studio.engine.reporting import AUTHORITY, STATUSES
from studio.engine.validator_core import ValidationRunResult, validate_compiler_result

INSPECTION_ID = "inspection.sdlc_studio.validation"
INSPECTION_SOURCE_PATHS = (
    "studio/engine/validation_inspection.py",
    "studio/docs/contracts/validation-result-ir-contract.md",
    "studio/docs/contracts/visual-orchestration-prototype.md",
)
VALID_CHECK_TYPES = ("yaml_parse", "path_exists", "path_scope", "relationship_target", "doctor", "lint", "policy", "custom")
VALID_TARGET_TYPES = ("edge", "github", "graph", "node", "path", "plane", "registry_entity", "stage", "workflow")
GROUP_BY_FIELDS = ("status", "check_type", "target_type")


class ValidationInspectionInputError(ValueError):
    """Raised for unsupported filters or grouping dimensions."""


def build_validation_inspection_from_sources(
    root: Any,
    *,
    status: str | None = None,
    check_type: str | None = None,
    target_type: str | None = None,
    group_by: str = "status",
) -> dict[str, Any]:
    """Compile, validate, derive canvas data, and inspect validation records in memory."""

    compiled = compile_studio_sources(root)
    validation = validate_compiler_result(compiled, root)
    canvas = build_canvas_view_model(compiled, validation)
    return build_validation_inspection_model(
        compiled,
        validation,
        canvas,
        status=status,
        check_type=check_type,
        target_type=target_type,
        group_by=group_by,
    )


def build_validation_inspection_model(
    compiled: CompilerResult,
    validation: ValidationRunResult,
    canvas: CanvasViewModel,
    *,
    status: str | None = None,
    check_type: str | None = None,
    target_type: str | None = None,
    group_by: str = "status",
) -> dict[str, Any]:
    """Build a filtered, deterministic inspection model from existing derived records."""

    filters = _validated_filters(status=status, check_type=check_type, target_type=target_type)
    if group_by not in GROUP_BY_FIELDS:
        raise ValidationInspectionInputError(f"invalid group_by: {group_by}")

    all_records = tuple(_inspection_record(record) for record in sorted(validation.results, key=_record_id))
    visible_records = tuple(
        record
        for record in all_records
        if (filters["status"] is None or record["status"] == filters["status"])
        and (filters["check_type"] is None or record["check_type"] == filters["check_type"])
        and (filters["target_type"] is None or record["target"]["ref_type"] == filters["target_type"])
    )
    inspection = {
        "id": INSPECTION_ID,
        "authority": AUTHORITY,
        "canvas_ref": str(canvas.canvas.get("id", "canvas.unknown")),
        "source_refs": _unique_source_refs([*_path_refs(INSPECTION_SOURCE_PATHS), *_source_refs(validation.report.get("source_refs"))]),
        "filters": filters,
        "group_by": group_by,
    }
    return {"inspection": inspection, "summary": _summary(all_records, visible_records), "groups": _groups(visible_records, group_by), "records": list(visible_records)}


def render_validation_inspection_text(model: dict[str, Any]) -> str:
    """Render a concise stdout-only validation inspection."""

    inspection = model["inspection"]
    summary = model["summary"]
    lines = [
        "Studio validation inspection: derived, non-authoritative output",
        f"inspection: {inspection['id']}",
        f"authority: {inspection['authority']}",
        f"canvas: {inspection['canvas_ref']}",
        f"group by: {inspection['group_by']}",
        _filters_line(inspection["filters"]),
        f"records: {summary['visible_records']} visible of {summary['total_records']} total",
    ]
    for status in STATUSES:
        lines.append(f"{status}: {summary['by_status'].get(status, 0)}")
    lines.append("groups:")
    lines.extend(f"- {group['label']}: {group['count']} ({', '.join(group['statuses'])})" for group in model["groups"])
    lines.append("records:")
    lines.extend(
        f"- {record['id']} [{record['status']}/{record['check_type']}] {record['target']['ref_type']}:{record['target']['ref']} - {record['summary']}"
        for record in model["records"]
    )
    lines.append("reminder: inspection data is transient stdout/in-memory view-model data only.")
    return "\n".join(lines) + "\n"


def _validated_filters(*, status: str | None, check_type: str | None, target_type: str | None) -> dict[str, str | None]:
    if status is not None and status not in STATUSES:
        raise ValidationInspectionInputError(f"invalid status: {status}")
    if check_type is not None and check_type not in VALID_CHECK_TYPES:
        raise ValidationInspectionInputError(f"invalid check_type: {check_type}")
    if target_type is not None and target_type not in VALID_TARGET_TYPES:
        raise ValidationInspectionInputError(f"invalid target_type: {target_type}")
    return {"status": status, "check_type": check_type, "target_type": target_type}


def _inspection_record(record: dict[str, Any]) -> dict[str, Any]:
    validation_ref = str(record.get("id", record.get("validation_ref", "validation.unknown")))
    target = _target_ref(record.get("target_ref"))
    messages = _messages(record.get("messages"))
    return {
        "id": f"inspection.record.{validation_ref.removeprefix('validation.')}",
        "validation_ref": validation_ref,
        "status": _status(record.get("status")),
        "check_type": _check_type(record.get("check_type")),
        "target": target,
        "messages": messages,
        "source_refs": _source_refs(record.get("source_refs")),
        "summary": _trim(messages[0]["text"], 180),
    }


def _groups(records: tuple[dict[str, Any], ...], group_by: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        key = str(record["target"]["ref_type"] if group_by == "target_type" else record[group_by])
        grouped.setdefault(key, []).append(record)
    return [
        {
            "id": f"inspection.group.{group_by}.{key}",
            "group_by": group_by,
            "key": key,
            "label": key.replace("_", " "),
            "count": len(grouped[key]),
            "statuses": [status for status in STATUSES if any(record["status"] == status for record in grouped[key])],
            "record_ids": sorted(record["id"] for record in grouped[key]),
        }
        for key in sorted(grouped)
    ]


def _summary(all_records: tuple[dict[str, Any], ...], visible_records: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    return {
        "total_records": len(all_records),
        "visible_records": len(visible_records),
        "by_status": {status: sum(1 for record in visible_records if record["status"] == status) for status in STATUSES},
        "by_check_type": {key: sum(1 for record in visible_records if record["check_type"] == key) for key in sorted({record["check_type"] for record in visible_records})},
        "by_target_type": {key: sum(1 for record in visible_records if record["target"]["ref_type"] == key) for key in sorted({record["target"]["ref_type"] for record in visible_records})},
    }


def _record_id(record: dict[str, Any]) -> str:
    return str(record.get("id", record.get("validation_ref", "")))


def _target_ref(value: Any) -> dict[str, str]:
    target = value if isinstance(value, dict) else {}
    return {"ref_type": str(target.get("ref_type", "path")), "ref": str(target.get("ref", "unknown"))}


def _messages(value: Any) -> list[dict[str, Any]]:
    messages = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            message = {"level": str(item.get("level", "info")), "text": _trim(str(item.get("text", "")), 500)}
            for key in ("path", "line", "column"):
                if key in item:
                    message[key] = item[key]
            messages.append(message)
    return messages or [{"level": "info", "text": "Validation status available without copied evidence."}]


def _source_refs(value: Any) -> list[dict[str, str]]:
    refs = []
    for item in value if isinstance(value, (list, tuple)) else []:
        if isinstance(item, str) and item:
            refs.append({"ref_type": "path", "ref": item})
        elif isinstance(item, dict) and item.get("ref"):
            ref = {"ref_type": str(item.get("ref_type", "path")), "ref": str(item["ref"])}
            if isinstance(item.get("summary"), str) and item["summary"]:
                ref["summary"] = _trim(item["summary"], 180)
            refs.append(ref)
    return _unique_source_refs(refs)


def _path_refs(paths: tuple[str, ...]) -> list[dict[str, str]]:
    return [{"ref_type": "path", "ref": path} for path in paths]


def _unique_source_refs(refs: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for ref in refs:
        unique.setdefault((ref["ref_type"], ref["ref"]), ref)
    return [unique[key] for key in sorted(unique)]


def _status(value: Any) -> str:
    status = str(value)
    return status if status in STATUSES else "not_run"


def _check_type(value: Any) -> str:
    check_type = str(value)
    return check_type if check_type in VALID_CHECK_TYPES else "custom"


def _filters_line(filters: dict[str, str | None]) -> str:
    applied = [f"{key}={value}" for key, value in filters.items() if value is not None]
    return "filters: " + (", ".join(applied) if applied else "none")


def _trim(value: str, limit: int) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."
