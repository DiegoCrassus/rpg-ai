"""Contract envelope builder and JSON Schema validation."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from jsonschema.validators import RefResolver
from rpg_platform.api.errors import AppError
from rpg_platform.time_utils import utcnow

CONTRACTS_DIR = Path(__file__).resolve().parents[4] / "shared" / "contracts"

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


def validate_contract_document(document: Any, contract_id: str) -> None:
    """Validate a document against its contract schema (no envelope wrapper)."""
    schema_file = CONTRACT_REGISTRY.get(contract_id)
    if schema_file is None:
        raise AppError("contract_unknown", f"Unknown contract: {contract_id}", 422)

    validator = build_validator(schema_file)
    try:
        validator.validate(document)
    except ValidationError as exc:
        raise AppError(
            "contract_validation_failed",
            f"Contract {contract_id} validation failed",
            422,
            details={"message": exc.message},
        ) from exc


def validate_envelope(document: Any, contract_id: str | None = None) -> None:
    envelope_validator = build_validator("envelope.v1.schema.json")
    try:
        envelope_validator.validate(document)
    except ValidationError as exc:
        raise AppError(
            "contract_invalid_envelope",
            "Envelope validation failed",
            422,
            details={"message": exc.message},
        ) from exc

    resolved = contract_id or document.get("contract")
    if not resolved:
        raise AppError("contract_missing", "Missing contract id", 422)

    schema_file = CONTRACT_REGISTRY.get(resolved)
    if schema_file is None:
        raise AppError("contract_unknown", f"Unknown contract: {resolved}", 422)

    validator = build_validator(schema_file)
    try:
        validator.validate(document)
    except ValidationError as exc:
        raise AppError(
            "contract_validation_failed",
            f"Contract {resolved} validation failed",
            422,
            details={"message": exc.message},
        ) from exc


def build_envelope(
    *,
    contract: str,
    contract_version: str,
    mesa_id: UUID,
    resource_id: UUID,
    entity_version: int,
    payload: dict[str, Any],
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> dict[str, Any]:
    now = utcnow().replace(microsecond=0)
    created = (created_at or now).isoformat().replace("+00:00", "Z")
    updated = (updated_at or now).isoformat().replace("+00:00", "Z")
    return {
        "contract": contract,
        "contract_version": contract_version,
        "meta": {
            "mesa_id": str(mesa_id),
            "resource_id": str(resource_id),
            "entity_version": entity_version,
            "created_at": created,
            "updated_at": updated,
        },
        "payload": payload,
    }


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contracts_dir_on_path() -> None:
    shared_root = CONTRACTS_DIR.parent
    shared_str = str(shared_root)
    if shared_str not in sys.path:
        sys.path.insert(0, shared_str)
