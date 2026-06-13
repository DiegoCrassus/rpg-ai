"""Tests for catalog stage_bindings SoT and generated pipeline/agents.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

DSL = Path(__file__).resolve().parent
SDLC_ROOT = DSL.parent
REPO_ROOT = SDLC_ROOT.parent
if str(SDLC_ROOT) not in sys.path:
    sys.path.insert(0, str(SDLC_ROOT))

from dsl import loader  # noqa: E402
from scripts.sdlc_sync_model import (  # noqa: E402
    PIPELINE_AGENTS_DESCRIPTION,
    PIPELINE_AGENTS_VERSION,
    build_pipeline_agents_shim,
)

CATALOG_PATH = REPO_ROOT / ".sdlc" / "manifest" / "catalog.yaml"
PIPELINE_PATH = REPO_ROOT / ".sdlc" / "pipeline" / "agents.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_catalog_has_stage_bindings():
    catalog = _load_yaml(CATALOG_PATH)
    bindings = catalog.get("stage_bindings")
    assert isinstance(bindings, list)
    assert len(bindings) >= 7
    ids = {item["id"] for item in bindings}
    assert {"planner", "architect", "implementer", "qa", "reviewer", "devops", "doctor"} <= ids


def test_generated_pipeline_matches_catalog():
    catalog = _load_yaml(CATALOG_PATH)
    pipeline = _load_yaml(PIPELINE_PATH)
    expected = build_pipeline_agents_shim(REPO_ROOT)

    assert pipeline.get("version") == PIPELINE_AGENTS_VERSION
    assert pipeline.get("description") == PIPELINE_AGENTS_DESCRIPTION
    assert pipeline.get("pipeline") == catalog.get("stage_bindings")
    assert pipeline.get("pipeline") == expected.get("pipeline")
    assert PIPELINE_PATH.read_text(encoding="utf-8").startswith(
        "# AUTO-GENERATED from .sdlc/manifest/catalog.yaml stage_bindings"
    )


def test_loader_returns_agents_from_catalog():
    loader._cache.clear()
    agents = loader.load_agents(str(REPO_ROOT))
    ids = {agent.id for agent in agents}
    assert {"planner", "architect", "implementer", "qa", "reviewer", "devops", "doctor"} <= ids

    catalog_bindings = _load_yaml(CATALOG_PATH).get("stage_bindings") or []
    assert len(agents) == len(catalog_bindings)

    skills = loader.load_skills(str(REPO_ROOT))
    skill_ids = {skill.id for skill in skills}
    assert "requirements-refinement" in skill_ids
    assert "structural-validation" in skill_ids
