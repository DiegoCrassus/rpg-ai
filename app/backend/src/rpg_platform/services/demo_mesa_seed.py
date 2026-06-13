"""Idempotent local demo mesa seed (D&D 5e template + example character)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import MesaStatus, ParticipantRole, ParticipantStatus
from rpg_platform.db.models import CharacterSheet, Mesa, MesaParticipant, SheetTemplate, User
from rpg_platform.services.audit import log_audit
from rpg_platform.services.characters import create_character
from rpg_platform.services.mesas import mesa_storage_paths
from rpg_platform.services.sheet_import_jobs import seed_dnd5e_template
from rpg_platform.services.storage import StorageService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DEMO_MESA_ID = uuid.UUID("b0000000-0000-4000-8000-000000000001")
ADMIN_ID = uuid.UUID("a0000000-0000-4000-8000-000000000001")
DEMO_MESA_NAME = "Mesa Demo — D&D 5e"
DEMO_CHARACTER_NAME = "Aelindra"


def demo_character_initial_values() -> dict[str, Any]:
    return {
        "identity": {
            "character_name": DEMO_CHARACTER_NAME,
            "species": "Elf",
            "class": "Wizard",
            "level": 3,
            "background": "Sage",
            "alignment": "tn",
        },
        "abilities": {
            "str": {"str_score": 8, "str_modifier": -1},
            "dex": {"dex_score": 14, "dex_modifier": 2},
            "con": {"con_score": 12, "con_modifier": 1},
            "int": {"int_score": 18, "int_modifier": 4},
            "wis": {"wis_score": 10, "wis_modifier": 0},
            "cha": {"cha_score": 12, "cha_modifier": 1},
        },
        "combat": {
            "armor_class": 12,
            "initiative": 2,
            "speed": 30,
            "size": "medium",
            "passive_perception": 10,
        },
        "proficiency_bonus": 2,
        "hit_points": {
            "hp_max": 18,
            "hp_current": 18,
            "hp_temp": 0,
            "hit_dice": "3d6",
        },
    }


@dataclass(frozen=True)
class DemoMesaSeedResult:
    mesa_id: uuid.UUID
    character_name: str
    created: bool


async def _get_seed_template(session: AsyncSession, mesa_id: uuid.UUID) -> SheetTemplate | None:
    result = await session.execute(
        select(SheetTemplate).where(
            SheetTemplate.mesa_id == mesa_id,
            SheetTemplate.is_seed.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def _get_demo_character(session: AsyncSession, mesa_id: uuid.UUID) -> CharacterSheet | None:
    result = await session.execute(
        select(CharacterSheet).where(
            CharacterSheet.mesa_id == mesa_id,
            CharacterSheet.character_name == DEMO_CHARACTER_NAME,
        )
    )
    return result.scalar_one_or_none()


async def _create_demo_mesa(session: AsyncSession, admin: User) -> Mesa:
    storage_root, manifest_path = mesa_storage_paths(DEMO_MESA_ID)

    mesa = Mesa(
        id=DEMO_MESA_ID,
        name=DEMO_MESA_NAME,
        description="Local development demo table with D&D 5e template and sample character.",
        rpg_system="D&D 5e",
        status=MesaStatus.IMPORTING,
        master_id=admin.id,
        storage_root=storage_root,
        manifest_storage_path=manifest_path,
    )
    session.add(mesa)
    session.add(
        MesaParticipant(
            mesa_id=mesa.id,
            user_id=admin.id,
            role=ParticipantRole.MASTER,
            status=ParticipantStatus.ACTIVE,
            joined_at=mesa.created_at,
        )
    )
    admin.master_mesa_count += 1
    await session.flush()

    await log_audit(
        session,
        actor_id=admin.id,
        mesa_id=mesa.id,
        action="mesa.created",
        resource_type="mesa",
        resource_id=mesa.id,
    )
    return mesa


async def ensure_demo_mesa(session: AsyncSession, storage: StorageService) -> DemoMesaSeedResult:
    admin = await session.get(User, ADMIN_ID)
    if admin is None:
        raise AppError(
            "admin_missing",
            "Admin user not found — run `make -C app migrate` first",
            500,
        )

    existing = await session.get(Mesa, DEMO_MESA_ID)
    created = False

    if existing is None:
        mesa = await _create_demo_mesa(session, admin)
        created = True
    else:
        mesa = existing

    template = await _get_seed_template(session, mesa.id)
    if template is None:
        template = await seed_dnd5e_template(session, storage, mesa=mesa, user=admin)

    character = await _get_demo_character(session, mesa.id)
    if character is None:
        await create_character(
            session,
            storage,
            mesa=mesa,
            template=template,
            owner=admin,
            character_name=DEMO_CHARACTER_NAME,
            initial_values=demo_character_initial_values(),
        )

    if mesa.status != MesaStatus.ACTIVE:
        mesa.status = MesaStatus.ACTIVE
        await session.flush()

    return DemoMesaSeedResult(
        mesa_id=mesa.id,
        character_name=DEMO_CHARACTER_NAME,
        created=created,
    )
