"""Append-only SDLC event store for Studio timeline and gateway hooks."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.infra.sdlc_obs.db import connect, default_db_path, init_db

SCHEMA_VERSION = "1.0"


def normalize_correlation(correlation: dict[str, Any] | None) -> dict[str, str]:
    raw = correlation or {}
    out: dict[str, str] = {}
    for key in ("run_id", "card", "branch", "session_id"):
        if raw.get(key):
            out[key] = str(raw[key])
    return out


def format_correlation_id(correlation: dict[str, Any] | None) -> str:
    norm = normalize_correlation(correlation)
    parts: list[str] = []
    if card := norm.get("card"):
        parts.append(f"card:{card}")
    if run_id := norm.get("run_id"):
        parts.append(f"run:{run_id}")
    if branch := norm.get("branch"):
        parts.append(f"branch:{branch}")
    if session_id := norm.get("session_id"):
        parts.append(f"session:{session_id}")
    return "|".join(parts) if parts else "none"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class EventStore:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path = Path(db_path) if db_path else default_db_path()
        init_db(self._db_path)

    @property
    def db_path(self) -> Path:
        return self._db_path

    def append_event(
        self,
        *,
        event_type: str,
        source: str,
        payload: dict[str, Any] | None = None,
        correlation: dict[str, Any] | None = None,
        category: str = "gateway",
        timestamp: str | None = None,
        event_id: str | None = None,
    ) -> dict[str, Any]:
        norm = normalize_correlation(correlation)
        event = {
            "schema_version": SCHEMA_VERSION,
            "event_id": event_id or f"evt_{uuid.uuid4().hex[:12]}",
            "event_type": event_type,
            "category": category,
            "timestamp": timestamp or _now_iso(),
            "source": source,
            "correlation_id": format_correlation_id(norm),
            "correlation": norm,
            "payload": payload or {},
        }
        with connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO sdlc_events (
                    event_id, schema_version, event_type, category, timestamp,
                    source, correlation_id, correlation_json, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"],
                    event["schema_version"],
                    event["event_type"],
                    event["category"],
                    event["timestamp"],
                    event["source"],
                    event["correlation_id"],
                    json.dumps(norm, ensure_ascii=False),
                    json.dumps(event["payload"], ensure_ascii=False),
                ),
            )
            conn.commit()
        return event

    def build_timeline(
        self,
        *,
        limit: int = 100,
        since: str | None = None,
        category: str | None = None,
        card: str | None = None,
        run_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if since:
            clauses.append("timestamp > ?")
            params.append(since)
        if category:
            clauses.append("category = ?")
            params.append(category)
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        if card:
            clauses.append("correlation_json LIKE ?")
            params.append(f'%"card": "{card}"%')
        if run_id:
            clauses.append("correlation_json LIKE ?")
            params.append(f'%"run_id": "{run_id}"%')

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT * FROM (
                SELECT * FROM sdlc_events {where}
                ORDER BY timestamp DESC LIMIT ?
            ) sub ORDER BY timestamp ASC
        """
        params.append(limit)

        with connect(self._db_path) as conn:
            rows = conn.execute(sql, params).fetchall()

        events: list[dict[str, Any]] = []
        for row in rows:
            correlation = json.loads(row["correlation_json"] or "{}")
            events.append(
                {
                    "schema_version": row["schema_version"],
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "category": row["category"],
                    "timestamp": row["timestamp"],
                    "source": row["source"],
                    "correlation_id": row["correlation_id"],
                    "correlation": correlation,
                    "payload": json.loads(row["payload_json"] or "{}"),
                }
            )
        return events

    def list_events(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self.build_timeline(**kwargs)
