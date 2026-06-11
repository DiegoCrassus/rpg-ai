"""S2 canvas projection: filter, ETag, and node detail helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from studio.engine.reporting import STATUSES
from studio_service.api.errors import StudioApiError


def canvas_etag(payload: dict[str, Any]) -> str:
    """Weak ETag from deterministic canvas JSON (filters excluded)."""

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    return f'W/"{digest}"'


def apply_canvas_filters(
    canvas: dict[str, Any],
    *,
    section: str | None = None,
    validation_status: str | None = None,
    entity_type: str | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    """Return filtered canvas view-model with applied filter metadata."""

    filters = _validated_filters(
        section=section,
        validation_status=validation_status,
        entity_type=entity_type,
        q=q,
    )
    nodes = list(canvas.get("nodes") or [])
    edges = list(canvas.get("edges") or [])
    overlays = list(canvas.get("overlays") or [])

    filtered_nodes = [_node for _node in nodes if _node_matches_filters(_node, filters)]
    visible_ids = {node["id"] for node in filtered_nodes}
    filtered_edges = [
        edge
        for edge in edges
        if edge.get("source") in visible_ids and edge.get("target") in visible_ids
    ]
    filtered_overlays = [_overlay for _overlay in overlays if _overlay_matches_status(_overlay, filters["validation_status"])]

    legend = _filtered_legend(filtered_nodes, filtered_overlays, canvas.get("legend") or {})
    return {
        "canvas": canvas.get("canvas") or {},
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "overlays": filtered_overlays,
        "sections": list(canvas.get("sections") or []),
        "legend": legend,
        "filters": filters,
        "meta": {
            "total_nodes": len(nodes),
            "filtered_nodes": len(filtered_nodes),
            "total_edges": len(edges),
            "filtered_edges": len(filtered_edges),
        },
    }


def find_canvas_node(canvas: dict[str, Any], display_id: str) -> dict[str, Any] | None:
    for node in canvas.get("nodes") or []:
        if node.get("id") == display_id:
            return node
    return None


def node_detail(canvas: dict[str, Any], display_id: str) -> dict[str, Any]:
    node = find_canvas_node(canvas, display_id)
    if node is None:
        raise StudioApiError(404, "CANVAS_NODE_NOT_FOUND", f"Canvas node not found: {display_id}")

    graph_node_id = str(node.get("graph_node_id", ""))
    overlay_ids = {summary["id"] for summary in node.get("validation_overlays") or []}
    related = [
        overlay
        for overlay in canvas.get("overlays") or []
        if overlay.get("id") in overlay_ids
        or (
            overlay.get("target", {}).get("ref_type") == "node"
            and overlay.get("target", {}).get("ref") == graph_node_id
        )
    ]
    return {"node": node, "overlays": sorted(related, key=lambda item: str(item.get("id", "")))}


def _validated_filters(
    *,
    section: str | None,
    validation_status: str | None,
    entity_type: str | None,
    q: str | None,
) -> dict[str, str | None]:
    if validation_status is not None and validation_status not in STATUSES:
        raise StudioApiError(
            400,
            "INVALID_CANVAS_FILTER",
            f"Unsupported validation_status: {validation_status}",
            details={"allowed": list(STATUSES)},
        )
    normalized_q = q.strip() if isinstance(q, str) and q.strip() else None
    return {
        "section": section.strip() if isinstance(section, str) and section.strip() else None,
        "validation_status": validation_status,
        "entity_type": entity_type.strip() if isinstance(entity_type, str) and entity_type.strip() else None,
        "q": normalized_q,
    }


def _node_matches_filters(node: dict[str, Any], filters: dict[str, str | None]) -> bool:
    if filters["section"] is not None and node.get("category") != filters["section"]:
        return False
    if filters["entity_type"] is not None and node.get("type") != filters["entity_type"]:
        return False
    if filters["validation_status"] is not None and not _node_matches_validation_status(node, filters["validation_status"]):
        return False
    if filters["q"] is not None and not _node_matches_search(node, filters["q"]):
        return False
    return True


def _node_matches_validation_status(node: dict[str, Any], status: str) -> bool:
    overlays = node.get("validation_overlays") or []
    if not overlays:
        return status == "not_run"
    return any(overlay.get("status") == status for overlay in overlays)


def _node_matches_search(node: dict[str, Any], query: str) -> bool:
    needle = query.casefold()
    haystacks = [
        str(node.get("label", "")),
        str(node.get("graph_node_id", "")),
        str(node.get("id", "")),
        str(node.get("type", "")),
        str(node.get("category", "")),
    ]
    for ref in node.get("source_refs") or []:
        haystacks.append(str(ref.get("ref", "")))
    return any(needle in value.casefold() for value in haystacks if value)


def _overlay_matches_status(overlay: dict[str, Any], status: str | None) -> bool:
    if status is None:
        return True
    return overlay.get("status") == status


def _filtered_legend(
    nodes: list[dict[str, Any]],
    overlays: list[dict[str, Any]],
    base_legend: dict[str, Any],
) -> dict[str, Any]:
    categories = sorted({str(node.get("category", "")) for node in nodes if node.get("category")})
    return {
        "categories": [{"id": category, "label": category} for category in categories],
        "validation_statuses": {
            status: sum(1 for overlay in overlays if overlay.get("status") == status) for status in STATUSES
        },
    }
