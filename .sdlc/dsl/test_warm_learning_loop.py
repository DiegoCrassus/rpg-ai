"""Tests for qa_evidence.py and warm learning loop wiring."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
SCRIPTS = ROOT / ".sdlc" / "scripts"
sys.path.insert(0, str(LEARNING))
sys.path.insert(0, str(SCRIPTS))

import event_store as es  # noqa: E402
import qa_evidence  # noqa: E402
import reward_engine as re  # noqa: E402


def test_qa_evidence_write_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    def fake_run(cmd, *, cwd, capture_output=True, text=True, check=False):
        output = "5 passed" if "pytest" in " ".join(cmd) else "Doctor summary: 1 passed"
        return 0, output

    monkeypatch.setattr(qa_evidence, "run_command", fake_run)
    path = qa_evidence.write_evidence(card="RPG-18", root=root, run_doctor=True)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["card"] == "RPG-18"
    assert data["tests"]["passed"] == 5
    assert data["verdict"] == "PASS"


def test_record_session_uses_qa_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    mem = root / ".sdlc" / "memory"
    learn = root / ".sdlc" / "learning" / "data"
    mem.mkdir(parents=True)
    learn.mkdir(parents=True)

    gate = {
        "gate_status": "open",
        "card": "RPG-18",
        "branch": "feature/RPG-18-x",
        "stage": "validation",
        "intent": "SDLC_META",
        "opened_at": "2026-06-13T12:00:00Z",
        "last_agent": "qa",
    }
    (mem / "session-gate.json").write_text(json.dumps(gate), encoding="utf-8")
    evidence = {
        "card": "RPG-18",
        "tests": {"passed": 10, "failed": 0, "exit_code": 0},
        "doctor": {"exit_code": 0},
        "verdict": "PASS",
    }
    (mem / "qa-evidence-RPG-18.json").write_text(json.dumps(evidence), encoding="utf-8")

    monkeypatch.setattr("learning_loop.ROOT", root)
    monkeypatch.setattr("learning_loop.GATE_PATH", mem / "session-gate.json")
    monkeypatch.setattr("learning_loop.HANDOFF_PATH", mem / "orchestrator-handoff.md")
    monkeypatch.setattr("learning_loop.LEDGER_PATH", root / ".sdlc" / "manifest" / "executions.jsonl")
    monkeypatch.setattr(es, "ROOT", root)
    events_file = learn / "events.jsonl"
    monkeypatch.setattr(es, "DEFAULT_EVENTS_PATH", events_file)

    import learning_loop  # noqa: E402

    args = argparse_namespace(agent="qa", gateway_block=None)
    assert learning_loop.cmd_record_from_session(args) == 0
    events = es.read_events(events_file)
    assert len(events) == 1
    assert events[0].tests_pass == 10
    assert events[0].reward >= 0.8


def test_gateway_block_lowers_reward() -> None:
    engine = re.RewardEngine()
    base, _ = engine.compute(re.RewardInput(tests_fail=0, tests_pass=5, doctor_exit=0))
    blocked, _ = engine.compute(
        re.RewardInput(tests_fail=0, tests_pass=5, doctor_exit=0, gateway_block=True)
    )
    assert blocked < base


def argparse_namespace(**kwargs):
    class NS:
        pass

    ns = NS()
    for key, val in kwargs.items():
        setattr(ns, key, val)
    return ns
