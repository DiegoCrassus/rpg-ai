"""Tests for slim L1 master-workflow.md index (RPG-21)."""

from __future__ import annotations

from pathlib import Path

MASTER_WORKFLOW = (
    Path(__file__).resolve().parent.parent / "process" / "master-workflow.md"
)
MAX_LINES = 120

REQUIRED_SECTIONS = (
    "## Documentation layers",
    "## Agreed principles",
    "## Step 0 — Entry (every session)",
    "operational_map",
    "lifecycle-model.yaml",
    "change-lifecycle.md",
    "communication-policy.md",
    "harness-v7-change-plan.md",
    ".cursor/agents",
    "stage_bindings",
    "catalog.yaml",
)


def test_master_workflow_line_count():
    lines = MASTER_WORKFLOW.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= MAX_LINES, f"master-workflow.md has {len(lines)} lines (max {MAX_LINES})"


def test_master_workflow_required_sections():
    text = MASTER_WORKFLOW.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_SECTIONS if marker not in text]
    assert not missing, f"missing required markers: {missing}"
