"""Tests for intent_rules.yaml classification."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
sys.path.insert(0, str(DSL))

from intent_rules import classify_from_rules  # noqa: E402


def test_empty_readonly():
    r = classify_from_rules("")
    assert r is not None
    assert r["intent"] == "READONLY"


def test_sdlc_meta():
    r = classify_from_rules("update .sdlc gate and workflow doctor")
    assert r["intent"] == "SDLC_META"


def test_feature_default():
    r = classify_from_rules("add user profile page")
    assert r["intent"] == "FEATURE"
