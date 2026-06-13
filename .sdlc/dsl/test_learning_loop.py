"""Tests for SDLC learning loop."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
sys.path.insert(0, str(LEARNING))

import event_store as es  # noqa: E402
import reward_engine as re  # noqa: E402
import schemas  # noqa: E402


def test_security_fail_negative_reward() -> None:
    engine = re.RewardEngine()
    reward, outcome = engine.compute(re.RewardInput(security_exit=1))
    assert reward == -1.0
    assert outcome.value == "failure"


def test_rollback_negative_one() -> None:
    engine = re.RewardEngine()
    reward, _ = engine.compute(re.RewardInput(rollback=True))
    assert reward == -1.0


def test_tests_fail_caps_at_zero() -> None:
    engine = re.RewardEngine()
    reward, outcome = engine.compute(re.RewardInput(tests_fail=2, tests_pass=0))
    assert reward <= 0.0
    assert outcome.value == "failure"


def test_all_green_high_reward() -> None:
    engine = re.RewardEngine()
    reward, outcome = engine.compute(
        re.RewardInput(
            tests_fail=0,
            tests_pass=10,
            lint_exit=0,
            doctor_exit=0,
            rework_count=0,
            tokens_in=5000,
            tokens_out=2000,
            human_approved=True,
        )
    )
    assert reward >= 0.8
    assert outcome.value == "success"


def test_intent_mapping() -> None:
    assert schemas.intent_to_task_type("FEATURE").value == "feature"
    assert schemas.intent_to_task_type("SDLC_META").value == "sdlc_meta"


def test_record_task_writes_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    (root / ".sdlc" / "learning" / "data").mkdir(parents=True)
    events_file = root / ".sdlc" / "learning" / "data" / "events.jsonl"
    monkeypatch.setattr(es, "ROOT", root)
    monkeypatch.setattr(es, "DEFAULT_EVENTS_PATH", events_file)
    event = es.record_task(
        card="RPG-99",
        agent="qa",
        stage="validation",
        intent="FEATURE",
        root=root,
    )
    assert event.reward >= -1.0
    events = es.read_events(events_file)
    assert len(events) == 1
    assert events[0].card == "RPG-99"
