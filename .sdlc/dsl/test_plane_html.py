"""Tests for Plane HTML formatting."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from plane_html import build_plan_html, convert_legacy_description, heading  # noqa: E402


def test_heading_has_editor_class():
    h = heading("Story")
    assert "editor-heading-block" in h


def test_convert_legacy_adds_classes():
    raw = "<div><h2>Story</h2><p>Hello world</p></div>"
    out = convert_legacy_description(raw)
    assert "editor-heading-block" in out
    assert "editor-paragraph-block" in out


def test_build_plan_html_structure():
    html = build_plan_html(
        {
            "task_name": "[AI][BACKEND] Example",
            "story": "One paragraph.",
            "scope": ["Item A", "Item B"],
            "next_step": "Architect review",
        }
    )
    assert html.startswith("<div>")
    assert "Task Name" in html
    assert "Item A" in html
