"""Bridge to ``app.infra.sdlc_obs`` store and collector."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from studio_service.config import Settings, get_settings


def _ensure_obs_imports(repo_root: Path) -> None:
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)


class ObsStoreService:
    def __init__(self, repo_root: Path, db_path: Path | None = None) -> None:
        _ensure_obs_imports(repo_root)
        from app.infra.sdlc_obs.collector import Collector  # type: ignore
        from app.infra.sdlc_obs.store import EventStore  # type: ignore

        settings = get_settings()
        resolved_db = db_path or settings.resolved_obs_db_path
        self._store = EventStore(resolved_db)
        self._collector = Collector(resolved_db)

    @property
    def db_path(self) -> Path:
        return self._store.db_path

    def append_event(self, **kwargs: Any) -> dict[str, Any]:
        event = self._store.append_event(**kwargs)
        return event

    def build_timeline(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self._store.build_timeline(**kwargs)

    def list_events(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self._store.list_events(**kwargs)

    def get_runs(self, limit: int = 100, stage: str | None = None) -> list[dict[str, Any]]:
        return self._collector.get_runs(limit=limit, stage=stage)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        runs = self._collector.get_runs(limit=500)
        for run in runs:
            if run["id"] == run_id:
                return run
        return None

    def get_metrics(self) -> dict[str, Any]:
        return {
            "kpis": self._collector.get_kpis(),
            "summary": self._collector.get_summary(),
        }


def get_obs_store(
    repo_root: Path,
    settings: Settings | None = None,
) -> ObsStoreService:
    cfg = settings or get_settings()
    return ObsStoreService(repo_root=repo_root, db_path=cfg.resolved_obs_db_path)
