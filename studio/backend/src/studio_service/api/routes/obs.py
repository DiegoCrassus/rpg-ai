from __future__ import annotations

import asyncio
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from studio_service.api.errors import StudioApiError
from studio_service.constants import PLANE_CARD_PREFIX
from studio_service.config import Settings, get_settings
from studio_service.deps import RepoRoot
from studio_service.schemas.events import ObsMetricsResponse, ObsRunsResponse, TimelineResponse
from studio_service.services.event_bus import EventBus, get_event_bus
from studio_service.services.obs_store import ObsStoreService, get_obs_store

router = APIRouter(prefix="/obs", tags=["s3-obs"])

VALID_CATEGORIES = frozenset({"gateway", "obs", "handoff", "gate"})


def _obs_bus(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> EventBus:
    return get_event_bus(repo_root, settings.resolved_obs_db_path)


def _obs_store(
    repo_root: RepoRoot,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ObsStoreService:
    return get_obs_store(repo_root, settings)


@router.get("/timeline", response_model=TimelineResponse)
def obs_timeline(
    bus: Annotated[EventBus, Depends(_obs_bus)],
    limit: int = Query(default=100, ge=1, le=500),
    since: str | None = Query(default=None, description="ISO-8601 lower bound"),
    category: str | None = Query(default=None, description="gateway | obs | handoff | gate"),
    card: str | None = Query(default=None, description=f"Filter by {PLANE_CARD_PREFIX} card"),
    run_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
) -> dict[str, Any]:
    if category and category not in VALID_CATEGORIES:
        raise StudioApiError(
            400,
            "INVALID_CATEGORY",
            f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
        )

    bus.poll_filesystem()
    events = bus.store.build_timeline(
        limit=limit,
        since=since,
        category=category,
        card=card,
        run_id=run_id,
        event_type=event_type,
    )
    return {"events": events, "count": len(events)}


@router.get("/runs", response_model=ObsRunsResponse)
def obs_runs(
    store: Annotated[ObsStoreService, Depends(_obs_store)],
    limit: int = Query(default=100, ge=1, le=500),
    stage: str | None = Query(default=None),
) -> dict[str, Any]:
    runs = store.get_runs(limit=limit, stage=stage)
    return {"runs": runs, "count": len(runs)}


@router.get("/runs/{run_id}")
def obs_run_detail(
    run_id: str,
    store: Annotated[ObsStoreService, Depends(_obs_store)],
) -> dict[str, Any]:
    run = store.get_run(run_id)
    if run is None:
        raise StudioApiError(404, "RUN_NOT_FOUND", f"No run found for id {run_id!r}")
    return run


@router.get("/metrics", response_model=ObsMetricsResponse)
def obs_metrics(store: Annotated[ObsStoreService, Depends(_obs_store)]) -> dict[str, Any]:
    metrics = store.get_metrics()
    return {"kpis": metrics["kpis"], "summary": metrics["summary"]}


async def _sse_stream(
    bus: EventBus,
    *,
    since: str | None,
    limit: int,
) -> Any:
    bus.poll_filesystem()
    replay = bus.store.build_timeline(limit=limit, since=since)
    if not replay:
        replay = bus.recent(limit=limit)
    if since:
        replay = [event for event in replay if event["timestamp"] >= since]

    queue = await bus.subscribe()
    try:
        for event in replay:
            payload = json.dumps(event, separators=(",", ":"))
            yield f"event: studio.obs\ndata: {payload}\n\n"

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
            except asyncio.TimeoutError:
                yield ": ping\n\n"
                bus.poll_filesystem()
                continue
            if event is None:
                break
            payload = json.dumps(event, separators=(",", ":"))
            yield f"event: studio.obs\ndata: {payload}\n\n"
    finally:
        bus.unsubscribe(queue)


@router.get("/events")
async def obs_events_sse(
    bus: Annotated[EventBus, Depends(_obs_bus)],
    since: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> StreamingResponse:
    generator = _sse_stream(bus, since=since, limit=limit)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/stream")
async def obs_stream_alias(
    bus: Annotated[EventBus, Depends(_obs_bus)],
    since: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> StreamingResponse:
    return await obs_events_sse(bus=bus, since=since, limit=limit)
