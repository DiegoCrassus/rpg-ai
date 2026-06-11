"""Mesa CRUD and lifecycle."""

from __future__ import annotations

import uuid
from typing import Any

from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import MesaStatus, ParticipantRole, ParticipantStatus
from rpg_platform.db.models import Mesa, MesaParticipant, User
from rpg_platform.policies.mesa import assert_master_cap, get_mesa_or_404
from rpg_platform.services.audit import log_audit
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def mesa_storage_paths(mesa_id: uuid.UUID) -> tuple[str, str]:
    root = f"{mesa_id}"
    manifest = f"{mesa_id}/manifest.json"
    return root, manifest


async def list_mesas_for_user(session: AsyncSession, user: User) -> list[Mesa]:
    if user.is_admin:
        result = await session.execute(select(Mesa).order_by(Mesa.created_at.desc()))
        return list(result.scalars().all())

    result = await session.execute(
        select(Mesa)
        .join(MesaParticipant, MesaParticipant.mesa_id == Mesa.id)
        .where(
            MesaParticipant.user_id == user.id,
            MesaParticipant.status == ParticipantStatus.ACTIVE,
        )
        .order_by(Mesa.created_at.desc())
    )
    return list(result.scalars().all())


async def create_mesa(
    session: AsyncSession,
    user: User,
    *,
    name: str,
    rpg_system: str,
    description: str | None = None,
) -> Mesa:
    await assert_master_cap(session, user)

    mesa_id = uuid.uuid4()
    storage_root, manifest_path = mesa_storage_paths(mesa_id)

    mesa = Mesa(
        id=mesa_id,
        name=name,
        description=description,
        rpg_system=rpg_system,
        status=MesaStatus.IMPORTING,
        master_id=user.id,
        storage_root=storage_root,
        manifest_storage_path=manifest_path,
    )
    session.add(mesa)

    participant = MesaParticipant(
        mesa_id=mesa.id,
        user_id=user.id,
        role=ParticipantRole.MASTER,
        status=ParticipantStatus.ACTIVE,
        joined_at=mesa.created_at,
    )
    session.add(participant)

    user.master_mesa_count += 1
    await session.flush()

    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=mesa.id,
        action="mesa.created",
        resource_type="mesa",
        resource_id=mesa.id,
    )
    return mesa


async def update_mesa(
    session: AsyncSession,
    mesa_id: uuid.UUID,
    *,
    name: str | None = None,
    description: str | None = None,
    rpg_system: str | None = None,
    settings: dict[str, Any] | None = None,
) -> Mesa:
    mesa = await get_mesa_or_404(session, mesa_id)
    if name is not None:
        mesa.name = name
    if description is not None:
        mesa.description = description
    if rpg_system is not None:
        mesa.rpg_system = rpg_system
    if settings is not None:
        merged = dict(mesa.settings)
        merged.update(settings)
        mesa.settings = merged
    await session.flush()
    return mesa


async def set_mesa_status(
    session: AsyncSession,
    mesa: Mesa,
    status: MesaStatus,
    actor_id: uuid.UUID,
) -> Mesa:
    old = mesa.status
    mesa.status = status

    if old != MesaStatus.ARCHIVED and status == MesaStatus.ARCHIVED:
        master = await session.get(User, mesa.master_id)
        if master:
            master.master_mesa_count = max(0, master.master_mesa_count - 1)
    elif old == MesaStatus.ARCHIVED and status != MesaStatus.ARCHIVED:
        master = await session.get(User, mesa.master_id)
        if master:
            if master.master_mesa_count >= 2:
                raise AppError("master_cap_exceeded", "BR-01: maximum 2 Mesas as Master", 409)
            master.master_mesa_count += 1

    await session.flush()
    await log_audit(
        session,
        actor_id=actor_id,
        mesa_id=mesa.id,
        action=f"mesa.status.{status.value}",
        resource_type="mesa",
        resource_id=mesa.id,
    )
    return mesa
