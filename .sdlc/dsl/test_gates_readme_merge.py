"""Tests for gates/README merge into gateways/README (RPG-23)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATEWAYS_README = ROOT / "gateways" / "README.md"
GATES_README = ROOT / "gates" / "README.md"


def test_gateways_readme_contains_write_gate_and_gateway_flow():
    text = GATEWAYS_README.read_text(encoding="utf-8")
    assert "## Write gate (mechanical ACL)" in text or "Write gate" in text
    assert "## Gateway flow" in text


def test_gates_readme_redirects_to_gateways():
    text = GATES_README.read_text(encoding="utf-8")
    assert "../gateways/README.md#write-gate-mechanical-acl" in text
    assert "Redirect" in text or "redirect" in text.lower()
