"""Mesa routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field
from rpg_platform.api.deps import CurrentUser, DbSession
from rpg_platform.db.enums import MesaStatus
from rpg_platform.policies.mesa import (
    assert_mesa_editable,
    get_mesa_or_404,
    require_master,
    require_member,
)
from rpg_platform.services.mesas import (
    create_mesa,
    list_mesas_for_user,
    set_mesa_status,
    update_mesa,
)

router = APIRouter(prefix="/mesas", tags=["mesas"])


class MesaResponse(BaseModel):
    id: str
    name: str
    description: str | None
    rpg_system: str
    status: str
    master_id: str
    settings: dict

    model_config = {"from_attributes": True}


class CreateMesaRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    rpg_system: str = Field(min_length=1, max_length=80)
    description: str | None = None


class UpdateMesaRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    description: str | None = None
    rpg_system: str | None = Field(default=None, max_length=80)
    settings: dict | None = None


def _mesa_response(mesa) -> MesaResponse:
    return MesaResponse(
        id=str(mesa.id),
        name=mesa.name,
        description=mesa.description,
        rpg_system=mesa.rpg_system,
        status=mesa.status.value,
        master_id=str(mesa.master_id),
        settings=mesa.settings,
    )


@router.get("", response_model=list[MesaResponse])
async def list_mesas(user: CurrentUser, session: DbSession) -> list[MesaResponse]:
    mesas = await list_mesas_for_user(session, user)
    return [_mesa_response(m) for m in mesas]


@router.post("", response_model=MesaResponse, status_code=201)
async def create_mesa_route(body: CreateMesaRequest, user: CurrentUser, session: DbSession) -> MesaResponse:
    mesa = await create_mesa(
        session,
        user,
        name=body.name,
        rpg_system=body.rpg_system,
        description=body.description,
    )
    return _mesa_response(mesa)


@router.get("/{mesa_id}", response_model=MesaResponse)
async def get_mesa(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> MesaResponse:
    await require_member(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    return _mesa_response(mesa)


@router.patch("/{mesa_id}", response_model=MesaResponse)
async def patch_mesa(
    mesa_id: uuid.UUID,
    body: UpdateMesaRequest,
    user: CurrentUser,
    session: DbSession,
) -> MesaResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    assert_mesa_editable(mesa)
    mesa = await update_mesa(
        session,
        mesa_id,
        name=body.name,
        description=body.description,
        rpg_system=body.rpg_system,
        settings=body.settings,
    )
    return _mesa_response(mesa)


@router.post("/{mesa_id}/pause", response_model=MesaResponse)
async def pause_mesa(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> MesaResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    mesa = await set_mesa_status(session, mesa, MesaStatus.PAUSED, user.id)
    return _mesa_response(mesa)


@router.post("/{mesa_id}/activate", response_model=MesaResponse)
async def activate_mesa(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> MesaResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    mesa = await set_mesa_status(session, mesa, MesaStatus.ACTIVE, user.id)
    return _mesa_response(mesa)


@router.post("/{mesa_id}/archive", response_model=MesaResponse)
async def archive_mesa(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> MesaResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    mesa = await set_mesa_status(session, mesa, MesaStatus.ARCHIVED, user.id)
    return _mesa_response(mesa)
