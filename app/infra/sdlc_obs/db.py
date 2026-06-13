"""SQLite helpers for SDLC observability."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def repo_root() -> Path:
    cur = Path(__file__).resolve()
    for _ in range(6):
        if (cur / ".sdlc").is_dir() and (cur / "Makefile").is_file():
            return cur
        cur = cur.parent
    return Path(__file__).resolve().parents[3]


def default_db_path() -> Path:
    env = os.environ.get("SDLC_OBS_DB") or os.environ.get("STUDIO_OBS_DB_PATH")
    if env:
        return Path(env)
    return repo_root() / "app" / "infra" / "sdlc_obs" / "data" / "sdlc_obs.db"


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    with connect(path) as conn:
        conn.executescript(schema)
        conn.commit()
    return path
