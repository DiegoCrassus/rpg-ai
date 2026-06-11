"""In-process event bus for Studio observability SSE fan-out."""

from __future__ import annotations

import asyncio
import threading
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from studio_service.services.obs_store import ObsStoreService
from studio_service.services.session_reader import read_handoff, read_session_gate


@dataclass
class EventBus:
    store: ObsStoreService
    repo_root: Path
    ring_size: int = 500
    _ring: deque[dict[str, Any]] = field(default_factory=deque, init=False)
    _subscribers: list[asyncio.Queue[dict[str, Any] | None]] = field(default_factory=list, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _handoff_mtime: float | None = field(default=None, init=False)
    _gate_mtime: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        recent = self.store.build_timeline(limit=self.ring_size)
        with self._lock:
            self._ring = deque(recent[-self.ring_size :], maxlen=self.ring_size)

    def publish(self, event: dict[str, Any], *, persist: bool = False) -> dict[str, Any]:
        if persist:
            event = self.store.append_event(
                event_type=event["event_type"],
                source=event["source"],
                payload=event.get("payload"),
                correlation=event.get("correlation"),
                category=event.get("category"),
                timestamp=event.get("timestamp"),
                event_id=event.get("event_id"),
            )
        with self._lock:
            self._ring.append(event)
            subscribers = list(self._subscribers)
        for queue in subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass
        return event

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            items = list(self._ring)
        return items[-limit:]

    async def subscribe(self) -> asyncio.Queue[dict[str, Any] | None]:
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(maxsize=256)
        with self._lock:
            self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any] | None]) -> None:
        with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def poll_filesystem(self) -> list[dict[str, Any]]:
        """Detect handoff/gate changes and emit synthetic events."""

        emitted: list[dict[str, Any]] = []
        gate_path = self.repo_root / ".sdlc/memory/session-gate.json"
        handoff_path = self.repo_root / ".sdlc/memory/orchestrator-handoff.md"

        gate_data = read_session_gate(self.repo_root)
        correlation = _correlation_from_gate(gate_data.get("gate") or {})

        if gate_path.is_file():
            mtime = gate_path.stat().st_mtime
            if self._gate_mtime is not None and mtime > self._gate_mtime:
                event = self.store.append_event(
                    event_type="session.gate_changed",
                    source="session_watcher",
                    category="gate",
                    correlation=correlation,
                    payload={
                        "gate_open": (gate_data.get("gate") or {}).get("gate_status") == "open",
                        "card": correlation.get("card"),
                        "branch": correlation.get("branch"),
                        "stage": (gate_data.get("gate") or {}).get("stage"),
                    },
                )
                emitted.append(self.publish(event))
            self._gate_mtime = mtime
        else:
            self._gate_mtime = None

        if handoff_path.is_file():
            mtime = handoff_path.stat().st_mtime
            if self._handoff_mtime is not None and mtime > self._handoff_mtime:
                handoff = read_handoff(self.repo_root)
                routing = (handoff.get("sections") or {}).get("Routing", {})
                session = (handoff.get("sections") or {}).get("Session", {})
                corr = dict(correlation)
                if card := session.get("Card"):
                    corr.setdefault("card", card)
                event = self.store.append_event(
                    event_type="handoff.updated",
                    source="handoff_watcher",
                    category="handoff",
                    correlation=corr,
                    payload={
                        "next_agent": routing.get("Next agent"),
                        "stage_complete": routing.get("Stage complete"),
                        "card": corr.get("card"),
                        "previous_agent": routing.get("Previous agent"),
                    },
                )
                emitted.append(self.publish(event))
            self._handoff_mtime = mtime
        else:
            self._handoff_mtime = None

        return emitted


def _correlation_from_gate(gate: dict[str, Any]) -> dict[str, Any]:
    correlation: dict[str, Any] = {}
    if card := gate.get("card"):
        correlation["card"] = str(card)
    if branch := gate.get("branch"):
        correlation["branch"] = str(branch)
    return correlation


_bus: EventBus | None = None
_bus_key: tuple[str, str] | None = None


def get_event_bus(repo_root: Path, db_path: Path | None = None) -> EventBus:
    global _bus, _bus_key
    key = (str(repo_root.resolve()), str(db_path) if db_path else "")
    if _bus is None or _bus_key != key:
        store = ObsStoreService(repo_root=repo_root, db_path=db_path)
        _bus = EventBus(store=store, repo_root=repo_root)
        _bus.poll_filesystem()
        _bus_key = key
    return _bus


def reset_event_bus() -> None:
    global _bus, _bus_key
    _bus = None
    _bus_key = None
