"""Shared contract validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.shared.contracts.validate_contracts import (
    CONTRACT_REGISTRY,
    CONTRACTS_DIR,
    validate_document,
    validate_file,
    validate_seed_files,
)

SHARED_ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = SHARED_ROOT / "seeds" / "dnd5e" / "schema.json"

MESA_ID = "11111111-1111-4111-8111-111111111111"
RESOURCE_ID = "22222222-2222-4222-8222-222222222222"
USER_ID = "33333333-3333-4333-8333-333333333333"
TEMPLATE_ID = "44444444-4444-4444-8444-444444444444"
JOB_ID = "55555555-5555-4555-8555-555555555555"
NOW = "2026-06-11T12:00:00Z"


def _meta(entity_version: int = 1) -> dict:
    return {
        "mesa_id": MESA_ID,
        "resource_id": RESOURCE_ID,
        "entity_version": entity_version,
        "created_at": NOW,
        "updated_at": NOW,
    }


def _envelope(contract: str, payload: dict, entity_version: int = 1) -> dict:
    return {
        "contract": contract,
        "contract_version": "1.0.0",
        "meta": _meta(entity_version),
        "payload": payload,
    }


@pytest.mark.parametrize("schema_file", sorted(CONTRACT_REGISTRY.values()))
def test_schema_files_exist_and_parse(schema_file: str) -> None:
    path = CONTRACTS_DIR / schema_file
    assert path.is_file(), f"missing schema {schema_file}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("$schema"), f"{schema_file} missing $schema"


def test_envelope_schema_exists() -> None:
    path = CONTRACTS_DIR / "envelope.v1.schema.json"
    assert path.is_file()


def test_dnd5e_seed_validates() -> None:
    assert SEED_PATH.is_file()
    assert validate_seed_files() == []
    validate_file(SEED_PATH)


def test_example_character_sheet_envelope() -> None:
    doc = _envelope(
        "rpg.character-sheet",
        {
            "template_id": TEMPLATE_ID,
            "template_entity_version": 1,
            "values": {"character_name": "Aragorn", "str_score": 18},
        },
    )
    validate_document(doc, "rpg.character-sheet")


def test_example_character_meta_envelope() -> None:
    doc = _envelope(
        "rpg.character-meta",
        {
            "character_name": "Aragorn",
            "owner_id": USER_ID,
            "template_id": TEMPLATE_ID,
            "status": "active",
            "visibility": "owner_only",
        },
    )
    validate_document(doc, "rpg.character-meta")


def test_example_document_meta_envelope() -> None:
    doc = _envelope(
        "rpg.document-meta",
        {
            "title": "Barovia — Village of Barovia",
            "type": "location",
            "tags": ["barovia", "village"],
            "visibility": "all_players",
            "visibility_targets": [],
            "character_sheet_id": None,
            "content_format": "markdown",
            "created_by": USER_ID,
        },
    )
    validate_document(doc, "rpg.document-meta")


def test_example_campaign_manifest_envelope() -> None:
    doc = _envelope(
        "rpg.campaign-manifest",
        {
            "mesa_id": MESA_ID,
            "mesa_name": "Curse of Strahd",
            "rpg_system": "D&D 5e",
            "entity_version": 5,
            "counts": {
                "templates": 2,
                "characters": 5,
                "documents": 42,
                "assets": 3,
            },
            "updated_at": NOW,
        },
    )
    validate_document(doc, "rpg.campaign-manifest")


def test_example_structured_document_envelope() -> None:
    doc = _envelope(
        "rpg.structured-document",
        {
            "title": "Strahd von Zarovich",
            "sections": [
                {"key": "description", "content": "Vampire lord of Barovia."},
                {"key": "motivation", "content": "Escape his domain."},
            ],
        },
    )
    validate_document(doc, "rpg.structured-document")


def test_example_sheet_import_proposal() -> None:
    proposal = {
        "job_id": JOB_ID,
        "detected_system": "dnd5e_2024",
        "detection_confidence": 0.94,
        "source_pages": 2,
        "template_proposal": {
            "name": "D&D 5e Character (imported)",
            "slug": "dnd5e-character-imported",
            "fields": [
                {"key": "character_name", "type": "text", "label": "Name", "required": True}
            ],
        },
        "field_confidence": [
            {"key": "character_name", "confidence": 0.98, "source_region": "page1:identity"}
        ],
        "warnings": [],
        "requires_review": True,
    }
    validate_document(proposal, "rpg.sheet-import-proposal")
