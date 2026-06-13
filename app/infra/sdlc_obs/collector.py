"""Run-level metrics collector for SDLC observability."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.infra.sdlc_obs.db import connect, default_db_path, init_db, repo_root

OBS_STATE = repo_root() / ".sdlc_obs_state.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class Collector:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path = Path(db_path) if db_path else default_db_path()
        init_db(self._db_path)

    @property
    def db_path(self) -> Path:
        return self._db_path

    def start(
        self,
        *,
        task_name: str,
        stage: str = "implementation",
        agent: str = "implementer",
        task_tags: list[str] | None = None,
        card: str = "",
        branch: str = "",
        session_id: str = "",
    ) -> str:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        tags = json.dumps(task_tags or ["[AI]"])
        with connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO sdlc_runs (
                    id, task_name, stage, agent, task_tags, started_at,
                    completion_status, card, branch, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, 'running', ?, ?, ?)
                """,
                (run_id, task_name, stage, agent, tags, _now_iso(), card, branch, session_id),
            )
            conn.commit()
        OBS_STATE.write_text(json.dumps({"run_id": run_id}, indent=2) + "\n", encoding="utf-8")
        return run_id

    def end(
        self,
        run_id: str,
        *,
        completion_status: str = "completed",
        duration_ms: int = 0,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        tool_calls_total: int = 0,
        tool_calls_success: int = 0,
        tool_calls_failed: int = 0,
        tests_passed: int = 0,
        tests_failed: int = 0,
        doctor_exit_code: int | None = None,
        hallucination_flag: bool = False,
    ) -> dict[str, Any]:
        with connect(self._db_path) as conn:
            conn.execute(
                """
                UPDATE sdlc_runs SET
                    ended_at = ?, completion_status = ?, duration_ms = ?,
                    tokens_input = ?, tokens_output = ?, cost_usd = ?,
                    tool_calls_total = ?, tool_calls_success = ?, tool_calls_failed = ?,
                    tests_passed = ?, tests_failed = ?, doctor_exit_code = ?,
                    hallucination_flag = ?
                WHERE id = ?
                """,
                (
                    _now_iso(),
                    completion_status,
                    duration_ms,
                    tokens_input,
                    tokens_output,
                    cost_usd,
                    tool_calls_total,
                    tool_calls_success,
                    tool_calls_failed,
                    tests_passed,
                    tests_failed,
                    doctor_exit_code,
                    1 if hallucination_flag else 0,
                    run_id,
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM sdlc_runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else {"id": run_id}

    def record(self, **kwargs: Any) -> str:
        run_id = self.start(
            task_name=str(kwargs.get("task_name", "[AI] task")),
            stage=str(kwargs.get("stage", "implementation")),
            agent=str(kwargs.get("agent", "implementer")),
            task_tags=list(kwargs.get("task_tags") or ["[AI]"]),
        )
        self.end(
            run_id,
            completion_status=str(kwargs.get("completion_status", "completed")),
            duration_ms=int(kwargs.get("duration_ms") or 0),
            tokens_input=int(kwargs.get("tokens_input") or 0),
            tokens_output=int(kwargs.get("tokens_output") or 0),
            cost_usd=float(kwargs.get("cost_usd") or 0.0),
            tool_calls_total=int(kwargs.get("tool_calls_total") or 0),
            tool_calls_success=int(kwargs.get("tool_calls_success") or 0),
            tool_calls_failed=int(kwargs.get("tool_calls_failed") or 0),
            tests_passed=int(kwargs.get("tests_passed") or 0),
            tests_failed=int(kwargs.get("tests_failed") or 0),
            doctor_exit_code=kwargs.get("doctor_exit_code"),
            hallucination_flag=bool(kwargs.get("hallucination_flag")),
        )
        return run_id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with connect(self._db_path) as conn:
            row = conn.execute("SELECT * FROM sdlc_runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None

    def get_runs(self, limit: int = 100, stage: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM sdlc_runs"
        params: list[Any] = []
        if stage:
            sql += " WHERE stage = ?"
            params.append(stage)
        sql += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        with connect(self._db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_kpis(self) -> dict[str, Any]:
        with connect(self._db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM sdlc_runs").fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM sdlc_runs WHERE completion_status = 'completed'"
            ).fetchone()[0]
            cost = conn.execute("SELECT COALESCE(SUM(cost_usd), 0) FROM sdlc_runs").fetchone()[0]
            tools = conn.execute(
                "SELECT COALESCE(SUM(tool_calls_total), 0), COALESCE(SUM(tool_calls_success), 0) FROM sdlc_runs"
            ).fetchone()
            halluc = conn.execute(
                "SELECT COUNT(*) FROM sdlc_runs WHERE hallucination_flag = 1"
            ).fetchone()[0]
        tool_total, tool_ok = tools or (0, 0)
        return {
            "total_runs": total,
            "completed_runs": completed,
            "completion_rate": round(completed / total, 4) if total else 0.0,
            "total_cost_usd": round(float(cost or 0), 6),
            "tool_success_rate": round(tool_ok / tool_total, 4) if tool_total else 0.0,
            "hallucination_rate": round(halluc / total, 4) if total else 0.0,
        }

    def get_summary(self) -> list[dict[str, Any]]:
        with connect(self._db_path) as conn:
            rows = conn.execute("SELECT * FROM sdlc_metrics ORDER BY stage, agent").fetchall()
        return [dict(row) for row in rows]
