"""Demo mesa seed idempotency tests."""

import pytest
from rpg_platform.db.enums import MesaStatus, UserStatus
from rpg_platform.db.models import CharacterSheet, Mesa, SheetTemplate, User
from rpg_platform.services.demo_mesa_seed import (
    ADMIN_ID,
    DEMO_CHARACTER_NAME,
    DEMO_MESA_ID,
    ensure_demo_mesa,
)
from rpg_platform.services.storage import StorageService
from sqlalchemy import func, select


async def _seed_admin(session) -> User:
    admin = User(
        id=ADMIN_ID,
        email="admin@rpg.local",
        display_name="Admin",
        status=UserStatus.ACTIVE,
        is_admin=True,
        master_mesa_count=0,
    )
    session.add(admin)
    await session.flush()
    return admin


@pytest.mark.asyncio
async def test_ensure_demo_mesa_idempotent(db_session):
    admin = await _seed_admin(db_session)
    storage = StorageService(use_memory=True)

    result1 = await ensure_demo_mesa(db_session, storage)
    await db_session.commit()
    await db_session.refresh(admin)

    result2 = await ensure_demo_mesa(db_session, storage)
    await db_session.commit()
    await db_session.refresh(admin)

    mesa_count = await db_session.scalar(select(func.count()).select_from(Mesa))
    char_count = await db_session.scalar(
        select(func.count())
        .select_from(CharacterSheet)
        .where(CharacterSheet.mesa_id == DEMO_MESA_ID)
    )
    template_count = await db_session.scalar(
        select(func.count())
        .select_from(SheetTemplate)
        .where(SheetTemplate.mesa_id == DEMO_MESA_ID, SheetTemplate.is_seed.is_(True))
    )

    mesa = await db_session.get(Mesa, DEMO_MESA_ID)
    template = (
        await db_session.execute(
            select(SheetTemplate).where(
                SheetTemplate.mesa_id == DEMO_MESA_ID,
                SheetTemplate.is_seed.is_(True),
            )
        )
    ).scalar_one()

    assert result1.created is True
    assert result2.created is False
    assert result1.mesa_id == DEMO_MESA_ID
    assert result1.character_name == DEMO_CHARACTER_NAME
    assert mesa_count == 1
    assert char_count == 1
    assert template_count == 1
    assert mesa is not None
    assert mesa.status == MesaStatus.ACTIVE
    assert template.is_seed is True
    assert admin.master_mesa_count == 1
