"""Tests for execution ledger (Harness v6 Layer 2)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".sdlc" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import execution_ledger as ledger  # noqa: E402


@pytest.fixture
def isolated_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ledger_root = tmp_path / "repo"
    ledger_root.mkdir()
    (ledger_root / ".sdlc" / "manifest").mkdir(parents=True)
    (ledger_root / ".sdlc" / "memory").mkdir(parents=True)
    ledger_file = ledger_root / ".sdlc" / "manifest" / "executions.jsonl"
    monkeypatch.setattr(ledger, "ROOT", ledger_root)
    monkeypatch.setattr(ledger, "LEDGER_PATH", ledger_file)
    monkeypatch.setattr(ledger, "MEMORY_DIR", ledger_root / ".sdlc" / "memory")
    monkeypatch.setattr(ledger, "SESSION_GATE", ledger_root / ".sdlc" / "memory" / "session-gate.json")
    return ledger_file


def test_compute_reward_gateway_block() -> None:
    r = ledger.compute_reward("gateway_block", {"handoff_complete": False})
    assert r == pytest.approx(0.4)


def test_compute_reward_stage_complete_qa_bonus() -> None:
    r = ledger.compute_reward(
        "stage_complete",
        {"stage_complete": "yes", "agent": "qa", "handoff_complete": True},
        prior_autofix_count=0,
    )
    assert r == pytest.approx(1.0)


def test_append_and_tail(isolated_ledger: Path) -> None:
    root = isolated_ledger.parents[2]
    ledger.append_event(
        {
            "card": "RPG-99",
            "event": "stage_complete",
            "agent": "qa",
            "outcome": {"handoff_complete": True},
            "reward": 1.0,
            "blockers": [],
        },
        root=root,
    )
    events = ledger.tail(5)
    assert len(events) == 1
    assert events[0]["card"] == "RPG-99"
    assert events[0]["v"] == 1


def test_snapshot_aggregates(isolated_ledger: Path) -> None:
    root = isolated_ledger.parents[2]
    ledger.append_event(
        {
            "card": "RPG-7",
            "event": "gateway_block",
            "reward": 0.7,
            "blockers": ["missing evidence"],
        },
        root=root,
    )
    ledger.append_event(
        {"card": "RPG-7", "event": "stage_complete", "reward": 1.0, "blockers": []},
        root=root,
    )
    out = ledger.snapshot("RPG-7", root=root)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["run_summary"]["gateway_blocks"] == 1
    assert len(data["stage_trace"]) == 2


def test_prune(isolated_ledger: Path) -> None:
    root = isolated_ledger.parents[2]
    for i in range(5):
        ledger.append_event(
            {"card": f"RPG-{i}", "event": "stage_complete", "blockers": []},
            root=root,
        )
    removed = ledger.prune_ledger(max_lines=3, path=isolated_ledger)
    assert removed == 2
    assert len(ledger.read_lines(isolated_ledger)) == 3
