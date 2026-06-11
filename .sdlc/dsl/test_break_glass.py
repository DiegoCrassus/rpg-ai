"""Tests for SDLC break-glass env gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

DSL = Path(__file__).resolve().parent
sys.path.insert(0, str(DSL))

from break_glass import is_break_glass, require_break_glass  # noqa: E402


def test_break_glass_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SDLC_BREAK_GLASS", raising=False)
    assert is_break_glass() is False
    assert require_break_glass("--force") is False


def test_break_glass_on_when_env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SDLC_BREAK_GLASS", "1")
    assert is_break_glass() is True
    assert require_break_glass("--force") is True
