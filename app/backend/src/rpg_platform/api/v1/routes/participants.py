"""Participants and invites routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from rpg_platform.api.deps import CurrentUser, DbSession
from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import InviteStatus, ParticipantStatus
from rpg_platform.db.models import Invite, MesaParticipant
from rpg_platform.policies.mesa import get_mesa_or_404, require_master, require_member
from rpg_platform.services.invites import accept_invite, create_invite
from sqlalchemy import select

router = APIRouter(tags=["participants"])


class ParticipantResponse(BaseModel):
    id: str
    user_id: str
    role: str
    status: str


class InviteResponse(BaseModel):
    id: str
    email: str
    status: str
    expires_at: str
    token: str | None = None


class CreateInviteRequest(BaseModel):
    email: EmailStr


class AcceptInviteRequest(BaseModel):
    token: str


@router.get("/mesas/{mesa_id}/participants", response_model=list[ParticipantResponse])
async def list_participants(
    mesa_id: uuid.UUID, user: CurrentUser, session: DbSession
) -> list[ParticipantResponse]:
    await require_member(session, mesa_id, user)
    result = await session.execute(
        select(MesaParticipant).where(
            MesaParticipant.mesa_id == mesa_id,
            MesaParticipant.status == ParticipantStatus.ACTIVE,
        )
    )
    return [
        ParticipantResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            role=p.role.value,
            status=p.status.value,
        )
        for p in result.scalars().all()
    ]


@router.delete("/mesas/{mesa_id}/participants/{participant_id}", status_code=204)
async def remove_participant(
    mesa_id: uuid.UUID,
    participant_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> None:
    await require_master(session, mesa_id, user)
    participant = await session.get(MesaParticipant, participant_id)
    if participant is None or participant.mesa_id != mesa_id:
        raise AppError("participant_not_found", "Participant not found", 404)
    participant.status = ParticipantStatus.REMOVED
    await session.flush()


@router.get("/mesas/{mesa_id}/invites", response_model=list[InviteResponse])
async def list_invites(
    mesa_id: uuid.UUID, user: CurrentUser, session: DbSession
) -> list[InviteResponse]:
    await require_master(session, mesa_id, user)
    result = await session.execute(select(Invite).where(Invite.mesa_id == mesa_id))
    return [
        InviteResponse(
            id=str(i.id),
            email=i.email,
            status=i.status.value,
            expires_at=i.expires_at.isoformat(),
        )
        for i in result.scalars().all()
    ]


@router.post("/mesas/{mesa_id}/invites", response_model=InviteResponse, status_code=201)
async def create_invite_route(
    mesa_id: uuid.UUID,
    body: CreateInviteRequest,
    user: CurrentUser,
    session: DbSession,
) -> InviteResponse:
    await require_master(session, mesa_id, user)
    await get_mesa_or_404(session, mesa_id)
    invite, token = await create_invite(
        session, mesa_id=mesa_id, email=body.email, created_by=user.id
    )
    return InviteResponse(
        id=str(invite.id),
        email=invite.email,
        status=invite.status.value,
        expires_at=invite.expires_at.isoformat(),
        token=token,
    )


@router.delete("/mesas/{mesa_id}/invites/{invite_id}", status_code=204)
async def cancel_invite(
    mesa_id: uuid.UUID,
    invite_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> None:
    await require_master(session, mesa_id, user)
    invite = await session.get(Invite, invite_id)
    if invite is None or invite.mesa_id != mesa_id:
        raise AppError("invite_not_found", "Invite not found", 404)
    invite.status = InviteStatus.CANCELLED
    await session.flush()


@router.post("/invites/accept")
async def accept_invite_route(
    body: AcceptInviteRequest,
    user: CurrentUser,
    session: DbSession,
) -> dict:
    participant = await accept_invite(session, token=body.token, user=user)
    return {
        "mesa_id": str(participant.mesa_id),
        "participant_id": str(participant.id),
        "role": participant.role.value,
    }
