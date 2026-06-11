"""Mesa membership and role policies."""

from __future__ import annotations

import uuid

from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import MesaStatus, ParticipantRole, ParticipantStatus, UserStatus
from rpg_platform.db.models import Mesa, MesaParticipant, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_or_404(session: AsyncSession, user_id: uuid.UUID) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise AppError("user_not_found", "User not found", 404)
    if user.status != UserStatus.ACTIVE:
        raise AppError("user_suspended", "User account is suspended", 403)
    return user


async def get_mesa_or_404(session: AsyncSession, mesa_id: uuid.UUID) -> Mesa:
    mesa = await session.get(Mesa, mesa_id)
    if mesa is None:
        raise AppError("mesa_not_found", "Mesa not found", 404)
    return mesa


async def get_participant(
    session: AsyncSession, mesa_id: uuid.UUID, user_id: uuid.UUID
) -> MesaParticipant | None:
    result = await session.execute(
        select(MesaParticipant).where(
            MesaParticipant.mesa_id == mesa_id,
            MesaParticipant.user_id == user_id,
            MesaParticipant.status == ParticipantStatus.ACTIVE,
        )
    )
    return result.scalar_one_or_none()


async def require_member(
    session: AsyncSession, mesa_id: uuid.UUID, user: User
) -> MesaParticipant:
    if user.is_admin:
        participant = await get_participant(session, mesa_id, user.id)
        if participant:
            return participant
        # Admin bypass — synthesize master-level access marker
        fake = MesaParticipant(
            mesa_id=mesa_id,
            user_id=user.id,
            role=ParticipantRole.MASTER,
            status=ParticipantStatus.ACTIVE,
        )
        return fake

    participant = await get_participant(session, mesa_id, user.id)
    if participant is None:
        raise AppError("mesa_forbidden", "Not a member of this Mesa", 403)
    return participant


async def require_master(session: AsyncSession, mesa_id: uuid.UUID, user: User) -> MesaParticipant:
    participant = await require_member(session, mesa_id, user)
    if not user.is_admin and participant.role != ParticipantRole.MASTER:
        raise AppError("mesa_master_required", "Master role required", 403)
    return participant


def assert_mesa_editable(mesa: Mesa) -> None:
    if mesa.status == MesaStatus.ARCHIVED:
        raise AppError("mesa_archived", "Mesa is archived", 409)


async def assert_master_cap(session: AsyncSession, user: User) -> None:
    if user.master_mesa_count >= 2:
        raise AppError("master_cap_exceeded", "BR-01: maximum 2 Mesas as Master", 409)
