"""Invite creation and acceptance."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import timedelta, timezone

from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import InviteStatus, ParticipantRole, ParticipantStatus
from rpg_platform.db.models import Invite, MesaParticipant, User
from rpg_platform.services.audit import log_audit
from rpg_platform.time_utils import utcnow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

INVITE_TTL_DAYS = 7


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


async def create_invite(
    session: AsyncSession,
    *,
    mesa_id: uuid.UUID,
    email: str,
    created_by: uuid.UUID,
) -> tuple[Invite, str]:
    token = generate_invite_token()
    invite = Invite(
        mesa_id=mesa_id,
        email=email.lower(),
        token_hash=hash_token(token),
        status=InviteStatus.PENDING,
        expires_at=utcnow() + timedelta(days=INVITE_TTL_DAYS),
        created_by=created_by,
    )
    session.add(invite)
    await session.flush()
    await log_audit(
        session,
        actor_id=created_by,
        mesa_id=mesa_id,
        action="invite.created",
        resource_type="invite",
        resource_id=invite.id,
        metadata={"email": email},
    )
    return invite, token


async def accept_invite(
    session: AsyncSession,
    *,
    token: str,
    user: User,
) -> MesaParticipant:
    token_h = hash_token(token)
    result = await session.execute(select(Invite).where(Invite.token_hash == token_h))
    invite = result.scalar_one_or_none()
    if invite is None:
        raise AppError("invite_not_found", "Invalid invite token", 404)

    now = utcnow()
    if invite.status != InviteStatus.PENDING:
        raise AppError("invite_used", "Invite already used or cancelled", 409)

    expires = invite.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        invite.status = InviteStatus.EXPIRED
        await session.flush()
        raise AppError("invite_expired", "Invite has expired", 410)

    if user.email.lower() != invite.email.lower():
        raise AppError("invite_email_mismatch", "BR-15: invite email must match account", 403)

    existing = await session.execute(
        select(MesaParticipant).where(
            MesaParticipant.mesa_id == invite.mesa_id,
            MesaParticipant.user_id == user.id,
        )
    )
    participant = existing.scalar_one_or_none()
    if participant is None:
        participant = MesaParticipant(
            mesa_id=invite.mesa_id,
            user_id=user.id,
            role=ParticipantRole.PLAYER,
            status=ParticipantStatus.ACTIVE,
            joined_at=now,
        )
        session.add(participant)
    else:
        participant.status = ParticipantStatus.ACTIVE
        participant.role = ParticipantRole.PLAYER
        participant.joined_at = now

    invite.status = InviteStatus.ACCEPTED
    invite.used_at = now
    invite.accepted_by = user.id
    await session.flush()

    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=invite.mesa_id,
        action="invite.accepted",
        resource_type="invite",
        resource_id=invite.id,
    )
    return participant
