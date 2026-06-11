"""Tests for canonical lifecycle model loading."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
sys.path.insert(0, str(DSL))

from gate import load_gate_config, repo_root  # noqa: E402
from lifecycle_model import (  # noqa: E402
    lifecycle_stage_ids,
    load_model,
    model_path,
)


def test_lifecycle_model_file_exists():
    root = repo_root()
    assert model_path(root).is_file()


def test_load_model_has_stages_and_write_policy():
    model = load_model()
    assert len(model.get("stages") or []) >= 10
    assert (model.get("write_policy") or {}).get("protected_prefixes")


def test_gate_config_reads_from_model():
    cfg = load_gate_config()
    assert "app/backend/" in (cfg.get("protected_prefixes") or [])
    assert "planning" in (cfg.get("stages") or {})


def test_lifecycle_stage_ids_include_ticket():
    assert "ticket" in lifecycle_stage_ids()


def test_write_policy_stages_map_to_lifecycle():
    model = load_model()
    lifecycle_ids = lifecycle_stage_ids()
    aliases = model.get("gate_stage_aliases") or {}
    for gate_key in (model.get("write_policy") or {}).get("stages") or {}:
        mapped = aliases.get(gate_key, [gate_key])
        for sid in mapped:
            assert sid in lifecycle_ids or gate_key in aliases
