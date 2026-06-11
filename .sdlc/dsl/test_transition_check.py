"""Tests for workflow transition checks."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
sys.path.insert(0, str(DSL))

from transition_check import transition_allowed  # noqa: E402


def test_fresh_start_allowed():
    ok, _ = transition_allowed("", "implementation")
    assert ok


def test_sdlc_meta_always_allowed():
    ok, _ = transition_allowed("implementation", "sdlc_meta")
    assert ok


def test_illegal_skip_architecture():
    ok, msg = transition_allowed("planning", "implementation")
    assert not ok
    assert "illegal" in msg.lower() or "transition" in msg.lower()
