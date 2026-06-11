from __future__ import annotations

import pytest

from studio.engine.mvp_test_skeleton import (
    EPIC_CARD,
    SKELETON_ENTRIES,
    SOURCE_CARD,
    VALIDATION_TYPES,
    build_mvp_test_skeleton,
    list_skeleton_entries,
)

EXPECTED_PHASES = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
ENTRY_IDS = tuple(spec[0] for spec in SKELETON_ENTRIES)


def test_mvp_test_skeleton_is_deterministic_and_shaped() -> None:
    first = build_mvp_test_skeleton()
    second = build_mvp_test_skeleton()

    assert first == second
    assert set(first) == {"skeleton", "summary", "entries", "validation_types"}
    assert first["skeleton"]["execution_mode"] == "non_executing_traceability_plan"
    assert first["skeleton"]["epic"] == EPIC_CARD
    assert first["skeleton"]["card"] == SOURCE_CARD
    assert first["summary"]["execution_claimed"] is False
    assert first["summary"]["phase_count"] == len(EXPECTED_PHASES)
    assert {entry["phase"] for entry in first["entries"] if entry["phase"] > 0} == EXPECTED_PHASES
    assert all(entry["status"] == "planned" for entry in first["entries"])
    assert [entry["id"] for entry in first["entries"]] == list(ENTRY_IDS)


def test_skeleton_references_plane_child_cards() -> None:
    model = build_mvp_test_skeleton()
    cards = set(model["summary"]["cards_referenced"])

    assert "INVES-54" in cards
    assert "INVES-75" in cards
    assert all(card.startswith("INVES-") for card in cards)
    for entry in model["entries"]:
        assert entry["cards"]
        assert entry["ac_ref"]


def test_skeleton_distinguishes_validation_types() -> None:
    model = build_mvp_test_skeleton()
    counts = model["summary"]["validation_types"]

    assert set(counts) == set(VALIDATION_TYPES)
    assert all(count > 0 for count in counts.values())
    assert any("doctor_gate" in entry["validation_types"] for entry in model["entries"])
    assert any("manual_review" in entry["validation_types"] for entry in model["entries"])


def test_list_skeleton_entries_matches_model() -> None:
    model = build_mvp_test_skeleton()
    assert list_skeleton_entries() == model["entries"]


@pytest.mark.parametrize("entry_id", ENTRY_IDS)
@pytest.mark.skip(reason="MVP skeleton stub — execute validation on scoped Plane card QA")
def test_mvp_skeleton_future_validation(entry_id: str) -> None:
    """Placeholder for future MVP validation mapped to epic acceptance criteria."""

    entries = {entry["id"]: entry for entry in build_mvp_test_skeleton()["entries"]}
    entry = entries[entry_id]
    assert entry["status"] == "planned"
    pytest.fail(f"Implement validation for {entry_id} during card QA, not skeleton mode")
