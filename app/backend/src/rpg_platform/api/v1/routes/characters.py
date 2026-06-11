"""Character sheet routes."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field
from rpg_platform.api.deps import CurrentUser, DbSession, StorageDep
from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import SheetVisibility
from rpg_platform.db.models import CharacterSheet, SheetTemplate
from rpg_platform.policies.mesa import get_mesa_or_404, require_member
from rpg_platform.policies.sheet import can_edit_sheet, can_read_sheet
from rpg_platform.services.characters import (
    create_character,
    list_characters,
    update_character_data,
)
from rpg_platform.services.documents import CAMPAIGNS_BUCKET

router = APIRouter(prefix="/mesas/{mesa_id}/characters", tags=["characters"])


class CharacterResponse(BaseModel):
    id: str
    character_name: str
    owner_id: str
    template_id: str
    visibility: str
    version: int
    status: str


class CreateCharacterRequest(BaseModel):
    template_id: uuid.UUID
    character_name: str = Field(min_length=1, max_length=120)
    visibility: SheetVisibility = SheetVisibility.OWNER_ONLY
    initial_values: dict[str, Any] | None = None


class UpdateCharacterRequest(BaseModel):
    character_name: str | None = None
    visibility: SheetVisibility | None = None


class CharacterDataRequest(BaseModel):
    values: dict[str, Any]


def _char_response(s: CharacterSheet) -> CharacterResponse:
    return CharacterResponse(
        id=str(s.id),
        character_name=s.character_name,
        owner_id=str(s.owner_id),
        template_id=str(s.template_id),
        visibility=s.visibility.value,
        version=s.version,
        status=s.status.value,
    )


async def _get_sheet_context(session, mesa_id, sheet_id, user):
    mesa = await get_mesa_or_404(session, mesa_id)
    participant = await require_member(session, mesa_id, user)
    sheet = await session.get(CharacterSheet, sheet_id)
    if sheet is None or sheet.mesa_id != mesa_id:
        raise AppError("character_not_found", "Character sheet not found", 404)
    return mesa, participant, sheet


@router.get("", response_model=list[CharacterResponse])
async def get_characters(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> list[CharacterResponse]:
    mesa = await get_mesa_or_404(session, mesa_id)
    participant = await require_member(session, mesa_id, user)
    sheets = await list_characters(session, mesa_id)
    visible = [s for s in sheets if can_read_sheet(s, mesa, user, participant)]
    return [_char_response(s) for s in visible]


@router.post("", response_model=CharacterResponse, status_code=201)
async def post_character(
    mesa_id: uuid.UUID,
    body: CreateCharacterRequest,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> CharacterResponse:
    await require_member(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    template = await session.get(SheetTemplate, body.template_id)
    if template is None or template.mesa_id != mesa_id:
        raise AppError("template_not_found", "Template not found", 404)
    sheet = await create_character(
        session,
        storage,
        mesa=mesa,
        template=template,
        owner=user,
        character_name=body.character_name,
        visibility=body.visibility,
        initial_values=body.initial_values,
    )
    return _char_response(sheet)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    mesa_id: uuid.UUID,
    character_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> CharacterResponse:
    mesa, participant, sheet = await _get_sheet_context(session, mesa_id, character_id, user)
    if not can_read_sheet(sheet, mesa, user, participant):
        raise AppError("character_forbidden", "Cannot view this character sheet", 403)
    return _char_response(sheet)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def patch_character(
    mesa_id: uuid.UUID,
    character_id: uuid.UUID,
    body: UpdateCharacterRequest,
    user: CurrentUser,
    session: DbSession,
) -> CharacterResponse:
    mesa, participant, sheet = await _get_sheet_context(session, mesa_id, character_id, user)
    if not can_edit_sheet(sheet, mesa, user, participant):
        raise AppError("character_forbidden", "Cannot edit this character sheet", 403)
    if body.character_name is not None:
        sheet.character_name = body.character_name
    if body.visibility is not None:
        sheet.visibility = body.visibility
    await session.flush()
    return _char_response(sheet)


@router.get("/{character_id}/data")
async def get_character_data(
    mesa_id: uuid.UUID,
    character_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    mesa, participant, sheet = await _get_sheet_context(session, mesa_id, character_id, user)
    if not can_read_sheet(sheet, mesa, user, participant):
        raise AppError("character_forbidden", "Cannot view this character sheet", 403)
    return await storage.get_json(CAMPAIGNS_BUCKET, sheet.storage_path)


@router.put("/{character_id}/data", response_model=CharacterResponse)
async def put_character_data(
    mesa_id: uuid.UUID,
    character_id: uuid.UUID,
    body: CharacterDataRequest,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> CharacterResponse:
    mesa, participant, sheet = await _get_sheet_context(session, mesa_id, character_id, user)
    if not can_edit_sheet(sheet, mesa, user, participant):
        raise AppError("character_forbidden", "Cannot edit this character sheet", 403)
    template = await session.get(SheetTemplate, sheet.template_id)
    assert template is not None
    sheet = await update_character_data(
        session, storage, sheet=sheet, mesa=mesa, template=template, user=user, values=body.values
    )
    return _char_response(sheet)


@router.get("/{character_id}/versions")
async def get_character_versions(
    mesa_id: uuid.UUID,
    character_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> list[dict]:
    from rpg_platform.db.models import CharacterSheetVersion
    from sqlalchemy import select

    mesa, participant, sheet = await _get_sheet_context(session, mesa_id, character_id, user)
    if not can_read_sheet(sheet, mesa, user, participant):
        raise AppError("character_forbidden", "Cannot view this character sheet", 403)
    result = await session.execute(
        select(CharacterSheetVersion)
        .where(CharacterSheetVersion.sheet_id == sheet.id)
        .order_by(CharacterSheetVersion.version.desc())
    )
    return [
        {"version": v.version, "storage_path": v.storage_path, "created_at": v.created_at.isoformat()}
        for v in result.scalars().all()
    ]
