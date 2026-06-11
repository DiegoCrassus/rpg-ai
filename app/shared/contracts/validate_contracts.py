"""Validate RPG platform JSON contracts against shared schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from jsonschema.validators import RefResolver

CONTRACTS_DIR = Path(__file__).resolve().parent
SHARED_ROOT = CONTRACTS_DIR.parent
SEEDS_DIR = SHARED_ROOT / "seeds"

CONTRACT_REGISTRY: dict[str, str] = {
    "rpg.sheet-template": "sheet-template.v1.schema.json",
    "rpg.character-sheet": "character-sheet.v1.schema.json",
    "rpg.document-meta": "document-meta.v1.schema.json",
    "rpg.character-meta": "character-meta.v1.schema.json",
    "rpg.campaign-manifest": "campaign-manifest.v1.schema.json",
    "rpg.sheet-import-proposal": "sheet-import-proposal.v1.schema.json",
    "rpg.structured-document": "structured-document.v1.schema.json",
}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _schema_store() -> dict[str, Any]:
    store: dict[str, Any] = {}
    for path in CONTRACTS_DIR.glob("*.schema.json"):
        data = _load_json(path)
        store[path.resolve().as_uri()] = data
        schema_id = data.get("$id")
        if isinstance(schema_id, str):
            store[schema_id] = data
    return store


def build_validator(schema_filename: str) -> Draft202012Validator:
    schema_path = CONTRACTS_DIR / schema_filename
    schema = _load_json(schema_path)
    resolver = RefResolver.from_schema(schema, store=_schema_store())
    return Draft202012Validator(schema, resolver=resolver)


def validate_document(document: Any, contract_id: str) -> None:
    schema_file = CONTRACT_REGISTRY.get(contract_id)
    if schema_file is None:
        raise ValueError(f"Unknown contract id: {contract_id}")
    validator = build_validator(schema_file)
    validator.validate(document)


def validate_file(path: Path, contract_id: str | None = None) -> None:
    document = _load_json(path)
    resolved_contract = contract_id or document.get("contract")
    if not resolved_contract:
        raise ValueError(f"Cannot infer contract for {path}")
    validate_document(document, resolved_contract)


def validate_seed_files() -> list[str]:
    errors: list[str] = []
    seed_path = SEEDS_DIR / "dnd5e" / "schema.json"
    try:
        validate_file(seed_path)
    except (ValidationError, ValueError, OSError) as exc:
        errors.append(f"{seed_path}: {exc}")
    return errors


def validate_example_envelopes(examples: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for label, payload in examples.items():
        contract_id = payload.get("contract")
        try:
            if not contract_id:
                raise ValueError("missing contract field")
            validate_document(payload, contract_id)
        except (ValidationError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
    return errors


def main() -> int:
    errors = validate_seed_files()
    if errors:
        for message in errors:
            print(f"FAIL: {message}", file=sys.stderr)
        return 1

    print(f"OK: validated seed {SEEDS_DIR / 'dnd5e' / 'schema.json'}")
    print(f"OK: {len(CONTRACT_REGISTRY)} contract schemas registered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
