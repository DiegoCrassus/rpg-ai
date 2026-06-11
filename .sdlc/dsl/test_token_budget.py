"""Tests for token budget ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

DSL = Path(__file__).resolve().parent
ROOT = DSL.parents[1]
sys.path.insert(0, str(DSL))

from token_budget import (  # noqa: E402
    TokenBudgetConfig,
    check_allow_action,
    extract_usage,
    load_config,
    record_usage,
    reset_session,
)


@pytest.fixture
def clean_ledger(tmp_path, monkeypatch):
    ledger_file = tmp_path / "token-budget.json"

    def _path(root=None):
        return ledger_file

    monkeypatch.setattr("token_budget.ledger_path", _path)
    monkeypatch.setattr("token_budget.repo_root", lambda start=None: ROOT)
    reset_session()
    yield ledger_file


def test_extract_usage_api_shape():
    inp, out, from_api = extract_usage(
        {"usage": {"input_tokens": 100, "output_tokens": 50}}
    )
    assert from_api
    assert inp == 100
    assert out == 50


def test_extract_usage_camel_case():
    inp, out, from_api = extract_usage(
        {"usage": {"inputTokens": 10, "outputTokens": 5}}
    )
    assert from_api
    assert inp == 10
    assert out == 5


def test_record_usage_estimates_when_no_api(clean_ledger, monkeypatch):
    monkeypatch.setattr(
        "token_budget.load_config",
        lambda root=None: TokenBudgetConfig(enforce="off", estimate_chars_per_token=4),
    )
    ledger = record_usage({"text": "abcd" * 10}, event="after-response")
    assert ledger.estimated_tokens >= 10
    assert ledger.total_tokens >= 10


def test_session_block_strict(clean_ledger, monkeypatch):
    cfg = TokenBudgetConfig(enforce="strict", session_budget=100, block_task_on_exceed=True)
    monkeypatch.setattr("token_budget.load_config", lambda root=None: cfg)
    record_usage({"usage": {"input_tokens": 90, "output_tokens": 20}}, event="after-response")
    ok, msg, _ = check_allow_action("subagent-start")
    assert not ok
    assert "session budget exceeded" in msg


def test_load_config_from_sdlc_yaml():
    cfg = load_config(ROOT)
    assert cfg.session_budget >= 1000
    assert cfg.enforce in ("strict", "warn", "off")


def test_reset_creates_session_id(clean_ledger):
    ledger = reset_session()
    assert ledger.session_id
    data = json.loads(clean_ledger.read_text(encoding="utf-8"))
    assert data["session_id"] == ledger.session_id
