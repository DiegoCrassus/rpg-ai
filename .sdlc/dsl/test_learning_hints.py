"""Smoke tests for learning_loop hints CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / ".sdlc" / "learning"
SCRIPTS = ROOT / ".sdlc" / "scripts"
sys.path.insert(0, str(LEARNING))
sys.path.insert(0, str(SCRIPTS))

import learning_loop  # noqa: E402
from policy_memory import ensure_seed  # noqa: E402


def _run_hints(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPTS / "learning_loop.py"), "hints", *args]
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, check=False)


def test_hints_exit_zero() -> None:
    result = _run_hints(
        "--json",
        "--agent",
        "implementer",
        "--stage",
        "implementation",
        "--task-type",
        "feature",
    )
    assert result.returncode == 0, result.stderr


def test_hints_json_valid_single_line() -> None:
    result = _run_hints(
        "--json",
        "--agent",
        "qa",
        "--stage",
        "validation",
        "--task-type",
        "FEATURE",
    )
    assert result.returncode == 0, result.stderr
    line = result.stdout.strip()
    assert "\n" not in line
    data = json.loads(line)
    assert isinstance(data, dict)


def test_hints_defaults_from_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    mem = root / ".sdlc" / "memory"
    mem.mkdir(parents=True)
    gate = {
        "gate_status": "open",
        "card": "RPG-19",
        "stage": "sdlc_meta",
        "intent": "SDLC_META",
        "last_agent": "implementer",
    }
    gate_path = mem / "session-gate.json"
    gate_path.write_text(json.dumps(gate), encoding="utf-8")

    monkeypatch.setattr(learning_loop, "ROOT", root)
    monkeypatch.setattr(learning_loop, "GATE_PATH", gate_path)

    args = argparse.Namespace(
        task_type=None,
        stage=None,
        agent=None,
        json=True,
    )
    assert learning_loop.cmd_hints(args) == 0


def test_ensure_seed_creates_policy_memory(tmp_path: Path) -> None:
    path = ensure_seed(tmp_path)
    assert path.is_file()
    assert path.name == "policy_memory.yaml"
    content = path.read_text(encoding="utf-8")
    assert "seed" in content
