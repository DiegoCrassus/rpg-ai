"""Contract validation rejection tests."""

import pytest
from rpg_platform.api.errors import AppError
from rpg_platform.contracts.validator import validate_envelope


def test_reject_invalid_envelope():
    with pytest.raises(AppError) as exc:
        validate_envelope({"contract": "rpg.sheet-template", "payload": {}})
    assert exc.value.status_code == 422
    assert exc.value.code == "contract_invalid_envelope"


def test_reject_unknown_contract():
    invalid = {
        "contract": "rpg.unknown",
        "contract_version": "1.0.0",
        "meta": {
            "mesa_id": "00000000-0000-4000-8000-000000000001",
            "resource_id": "00000000-0000-4000-8000-000000000002",
            "entity_version": 1,
            "created_at": "2026-06-11T00:00:00Z",
            "updated_at": "2026-06-11T00:00:00Z",
        },
        "payload": {},
    }
    with pytest.raises(AppError) as exc:
        validate_envelope(invalid)
    assert exc.value.code in ("contract_unknown", "contract_invalid_envelope", "contract_validation_failed")
