"""Tests for lifecycle shard drift and loader canonical paths."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
SDLC_ROOT = DSL.parent
sys.path.insert(0, str(SDLC_ROOT))
sys.path.insert(0, str(DSL))

from gate import repo_root  # noqa: E402
from lifecycle_shard_drift import (  # noqa: E402
    check_committed_plane_evidence,
    check_lifecycle_shard_drift,
)

from dsl import loader  # noqa: E402


def test_shard_drift_passes_on_repo():
    root = repo_root()
    fails = [m for lvl, m in check_lifecycle_shard_drift(root) if lvl == "FAIL"]
    assert not fails, fails


def test_no_committed_plane_evidence_templates():
    level, _ = check_committed_plane_evidence(repo_root())
    assert level == "PASS"


def test_loader_reads_lifecycle_model():
    root = str(repo_root())
    stages = loader.load_lifecycle(root)
    assert stages[0].id == "ticket"
    workflows = loader.load_workflows(root)
    ids = {w.id for w in workflows}
    assert "ticket_to_requirements" in ids
    assert "review_to_deployment" in ids
