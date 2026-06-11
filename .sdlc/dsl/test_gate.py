"""Tests for SDLC session gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

DSL = Path(__file__).resolve().parent
ROOT = DSL.parents[1]
sys.path.insert(0, str(DSL))

from gate import (  # noqa: E402
    check_write,
    check_write_simulated,
    close_gate,
    is_protected,
    load_gate_config,
    open_gate,
)


@pytest.fixture
def clean_gate(tmp_path, monkeypatch):
    gate_file = tmp_path / "session-gate.json"

    def _gate_path(root=None):
        return gate_file

    monkeypatch.setattr("gate.session_gate_path", _gate_path)
    monkeypatch.setattr("gate.repo_root", lambda start=None: ROOT)
    monkeypatch.setattr("core_config.gate_enforcement", lambda root=None: "strict")
    close_gate()
    yield gate_file
    close_gate()


def test_protected_paths():
    config = load_gate_config(ROOT)
    assert is_protected("app/backend/foo.py", config)
    assert is_protected("pyproject.toml", config)
    assert not is_protected(".cursor/rules/test.mdc", config)


def test_gate_closed_blocks_app(clean_gate):
    ok, msg = check_write("app/backend/main.py")
    assert not ok
    assert "Gate closed" in msg


def test_gate_open_allows_implementation(clean_gate):
    open_gate(card="RPG-99", branch="feature/RPG-99-test", stage="implementation")
    ok, msg = check_write("app/backend/main.py")
    assert ok, msg


def test_gate_open_blocks_wrong_stage(clean_gate):
    open_gate(card="RPG-99", branch="feature/RPG-99-test", stage="planning")
    ok, msg = check_write("app/backend/main.py")
    assert not ok
    assert "not allowed for stage" in msg


def test_sdlc_meta_allows_cursor(clean_gate):
    open_gate(card="RPG-99", branch="sdlc/meta", stage="sdlc_meta")
    ok, msg = check_write(".cursor/rules/orchestrator.mdc")
    assert ok, msg


def test_check_write_simulated_when_gate_closed(clean_gate):
    ok, msg = check_write_simulated("app/backend/foo.py", "implementation", ROOT)
    assert ok, msg
    assert "simulated" in msg.casefold() or "gate closed" in msg.casefold()


def test_gate_enforcement_off_allows_without_open_gate(clean_gate, monkeypatch):
    monkeypatch.setattr("gate.is_gate_enforcement_off", lambda root=None: True)
    ok, msg = check_write("app/backend/main.py")
    assert ok, msg
    assert "enforcement off" in msg.casefold()


def test_gate_enforcement_off_via_env(clean_gate, monkeypatch):
    monkeypatch.delenv("SDLC_GATES", raising=False)
    monkeypatch.setenv("SDLC_GATES", "off")
    from gate import gate_enforcement_mode  # noqa: E402

    assert gate_enforcement_mode(ROOT) == "off"
    ok, msg = check_write("pyproject.toml")
    assert ok, msg


def test_gate_enforcement_yaml_false_treated_as_off():
    """YAML parses bare `off` as false — gate_enforcement must still return off."""
    from core_config import gate_enforcement  # noqa: E402

    class _FakeCore:
        @staticmethod
        def gates(_root):
            return {"enforcement": False}

    import core_config as cc  # noqa: E402

    original = cc.gates
    cc.gates = _FakeCore.gates  # type: ignore[assignment]
    try:
        assert gate_enforcement(ROOT) == "off"
    finally:
        cc.gates = original  # type: ignore[assignment]
