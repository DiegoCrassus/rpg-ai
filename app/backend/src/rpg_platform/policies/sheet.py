"""Character sheet visibility policies."""

from __future__ import annotations

from rpg_platform.db.enums import ParticipantRole, SheetVisibility
from rpg_platform.db.models import CharacterSheet, Mesa, MesaParticipant, User


def can_read_sheet(
    sheet: CharacterSheet,
    mesa: Mesa,
    user: User,
    participant: MesaParticipant | None,
) -> bool:
    if user.is_admin:
        return True
    if participant is None:
        return False
    if participant.role == ParticipantRole.MASTER:
        return True
    if sheet.owner_id == user.id:
        return True
    if sheet.visibility == SheetVisibility.ALL_PLAYERS:
        return bool(mesa.settings.get("players_can_view_other_sheets"))
    if sheet.visibility == SheetVisibility.MESA_MASTERS:
        return participant.role == ParticipantRole.MASTER
    return False


def can_edit_sheet(
    sheet: CharacterSheet,
    mesa: Mesa,
    user: User,
    participant: MesaParticipant | None,
) -> bool:
    if user.is_admin:
        return True
    if participant is None:
        return False
    if participant.role == ParticipantRole.MASTER:
        return True
    if sheet.owner_id == user.id:
        return bool(mesa.settings.get("players_can_edit_own_sheet"))
    return False
