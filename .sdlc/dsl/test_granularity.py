"""Tests for Plane granularity validation."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
sys.path.insert(0, str(DSL))

from plane_granularity import validate_granularity  # noqa: E402


def test_rejects_fullstack_greenfield_epic():
    issue = {
        "name": "[AI][FULLSTACK] Build entire app",
        "description_html": "<p>Story scope task breakdown backend frontend</p>",
    }
    failures = validate_granularity(issue, intent="GREENFIELD", child_count=0)
    assert any("FULLSTACK" in f for f in failures)


def test_epic_needs_layers():
    issue = {
        "name": "[AI][EPIC] MarketPulse delivery",
        "description_html": "<p>Task Breakdown [AI][BACKEND] only</p>",
    }
    failures = validate_granularity(issue, intent="GREENFIELD", child_count=0)
    assert any("layers" in f for f in failures)


def test_epic_passes_with_breakdown_and_children():
    issue = {
        "name": "[AI][EPIC] MarketPulse delivery",
        "description_html": """
        <p>Task Breakdown</p>
        <ul>
          <li>RPG-26 [AI][BACKEND] API</li>
          <li>RPG-27 [AI][FRONTEND] UI</li>
          <li>RPG-28 [AI][INFRA] compose</li>
        </ul>
        """,
    }
    failures = validate_granularity(issue, intent="GREENFIELD", child_count=3)
    assert failures == []


def test_bugfix_skips_granularity():
    issue = {"name": "[AI][BACKEND] Fix login bug", "description_html": "<p>x</p>"}
    failures = validate_granularity(issue, intent="BUGFIX", child_count=0)
    assert failures == []
