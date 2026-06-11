"""Tests for write gate hook — protected-path-only enforcement."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
DSL = HOOKS.parents[1] / ".sdlc" / "dsl"
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))
if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

import gate as gate_mod  # noqa: E402
import sdlc_gate_hook as gate_hook  # noqa: E402
import sdlc_gateway_lib as gateway  # noqa: E402
import sdlc_pre_gateway as pre_gateway  # noqa: E402


def test_extract_write_path_supports_nested_arguments() -> None:
    payload = {"arguments": {"path": "docs/product/readme.md"}}
    assert gateway.extract_write_path(payload) == "docs/product/readme.md"


def test_gate_hook_allows_invalid_json_payload(capsys, monkeypatch) -> None:
    monkeypatch.setattr(gate_hook._gate, "is_gate_enforcement_off", lambda root: False)
    sys.stdin = io.StringIO("not-json{{{")
    with pytest.raises(SystemExit) as exc_info:
        gate_hook.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"


def test_gate_hook_allows_unprotected_path_when_gate_closed(capsys, monkeypatch) -> None:
    monkeypatch.setattr(gate_hook._gate, "is_gate_enforcement_off", lambda root: False)
    monkeypatch.setattr(gate_hook._gate, "load_gate_config", lambda root: {"protected_prefixes": ["app/backend/"]})
    monkeypatch.setattr(gate_hook._gate, "is_protected", lambda rel, cfg: rel.startswith("app/"))

    payload = json.dumps({"tool_input": {"path": "docs/product/README.md"}})
    sys.stdin = io.StringIO(payload)
    with pytest.raises(SystemExit) as exc_info:
        gate_hook.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"


def test_gate_hook_denies_protected_path_when_gate_closed(capsys, monkeypatch) -> None:
    monkeypatch.setattr(gate_hook._gate, "is_gate_enforcement_off", lambda root: False)
    monkeypatch.setattr(gate_hook._gate, "load_gate_config", lambda root: {"protected_prefixes": ["app/backend/"]})
    monkeypatch.setattr(gate_hook._gate, "is_protected", lambda rel, cfg: rel.startswith("app/"))
    monkeypatch.setattr(
        gate_hook._gate,
        "check_write",
        lambda rel, root: (False, "Gate closed"),
    )
    monkeypatch.setattr(
        gate_hook._gate,
        "load_session_gate",
        lambda root: gate_mod.SessionGate(card="RPG-99"),
    )

    payload = json.dumps({"tool_input": {"path": "app/backend/src/main.py"}})
    sys.stdin = io.StringIO(payload)
    with pytest.raises(SystemExit) as exc_info:
        gate_hook.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "deny"
    assert "protected path" in result["user_message"]


def test_gate_hook_bypasses_when_enforcement_off(capsys, monkeypatch) -> None:
    monkeypatch.setattr(gate_hook._gate, "is_gate_enforcement_off", lambda root: True)
    sys.stdin = io.StringIO(json.dumps({"tool_input": {"path": "app/backend/x.py"}}))
    with pytest.raises(SystemExit) as exc_info:
        gate_hook.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"


def test_pre_gateway_allows_invalid_json_payload(capsys, monkeypatch) -> None:
    monkeypatch.setattr(pre_gateway, "require_policy", lambda: {"pre_gateway": {}})
    monkeypatch.setattr(pre_gateway, "gate_enforcement_off", lambda: False)
    sys.stdin = io.StringIO("<<<broken")
    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"


def test_read_stdin_text_returns_empty_without_blocking(monkeypatch) -> None:
    import threading
    import time

    class BlockingReader:
        def isatty(self) -> bool:
            return False

        def read(self) -> str:
            time.sleep(5)
            return "{}"

    monkeypatch.setattr(gateway.sys, "stdin", BlockingReader())

    start = time.monotonic()
    assert gateway.read_stdin_text(timeout_seconds=0.1) == ""
    assert time.monotonic() - start < 1.0


def test_pre_gateway_allows_empty_stdin_without_hanging(capsys, monkeypatch) -> None:
    monkeypatch.setattr(pre_gateway, "require_policy", lambda: {"pre_gateway": {}})
    monkeypatch.setattr(pre_gateway, "gate_enforcement_off", lambda: True)
    monkeypatch.setattr(gateway, "read_stdin_text", lambda timeout_seconds=0.25: "")
    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"


def test_pre_gateway_skips_subagent_routing_when_enforcement_off(
    capsys, monkeypatch
) -> None:
    monkeypatch.setattr(pre_gateway, "require_policy", lambda: {"pre_gateway": {}})
    monkeypatch.setattr(pre_gateway, "gate_enforcement_off", lambda: True)
    sys.stdin = io.StringIO(json.dumps({"tool_input": {"subagent_type": "qa"}}))
    with pytest.raises(SystemExit) as exc_info:
        pre_gateway.main()
    assert exc_info.value.code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["permission"] == "allow"
