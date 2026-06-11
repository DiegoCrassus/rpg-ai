"""Character sheet service helpers."""

from __future__ import annotations

import uuid
from typing import Any

from rpg_platform.contracts.validator import build_envelope, sha256_hex, validate_envelope
from rpg_platform.db.enums import SheetStatus, SheetVisibility, StorageResourceType
from rpg_platform.db.models import (
    CharacterSheet,
    CharacterSheetVersion,
    Mesa,
    SheetTemplate,
    StorageFile,
    User,
)
from rpg_platform.services.audit import log_audit
from rpg_platform.services.storage import StorageService
from rpg_platform.time_utils import utcnow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

CAMPAIGNS_BUCKET = "campaigns"


async def list_characters(session: AsyncSession, mesa_id: uuid.UUID) -> list[CharacterSheet]:
    result = await session.execute(
        select(CharacterSheet)
        .where(CharacterSheet.mesa_id == mesa_id, CharacterSheet.status == SheetStatus.ACTIVE)
        .order_by(CharacterSheet.character_name)
    )
    return list(result.scalars().all())


async def create_character(
    session: AsyncSession,
    storage: StorageService,
    *,
    mesa: Mesa,
    template: SheetTemplate,
    owner: User,
    character_name: str,
    visibility: SheetVisibility = SheetVisibility.OWNER_ONLY,
    initial_values: dict[str, Any] | None = None,
) -> CharacterSheet:
    sheet_id = uuid.uuid4()
    data_path = f"{mesa.id}/characters/{sheet_id}/data.json"
    meta_path = f"{mesa.id}/characters/{sheet_id}/meta.json"

    data_envelope = build_envelope(
        contract="rpg.character-sheet",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=sheet_id,
        entity_version=1,
        payload={
            "template_id": str(template.id),
            "template_entity_version": template.version,
            "values": initial_values or {},
        },
    )
    meta_envelope = build_envelope(
        contract="rpg.character-meta",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=sheet_id,
        entity_version=1,
        payload={
            "character_name": character_name,
            "owner_id": str(owner.id),
            "template_id": str(template.id),
            "status": SheetStatus.ACTIVE.value,
            "visibility": visibility.value,
        },
    )
    validate_envelope(data_envelope)
    validate_envelope(meta_envelope)

    data_raw = await storage.put_json(CAMPAIGNS_BUCKET, data_path, data_envelope)
    meta_raw = await storage.put_json(CAMPAIGNS_BUCKET, meta_path, meta_envelope)
    now = utcnow()

    sheet = CharacterSheet(
        id=sheet_id,
        mesa_id=mesa.id,
        template_id=template.id,
        owner_id=owner.id,
        character_name=character_name,
        visibility=visibility,
        template_version=template.version,
        version=1,
        storage_path=data_path,
        meta_storage_path=meta_path,
    )
    session.add(sheet)
    session.add(
        CharacterSheetVersion(
            sheet_id=sheet_id,
            mesa_id=mesa.id,
            version=1,
            storage_path=data_path,
            checksum_sha256=sha256_hex(data_raw),
            created_by=owner.id,
        )
    )
    for path, raw, contract in [
        (data_path, data_raw, "rpg.character-sheet"),
        (meta_path, meta_raw, "rpg.character-meta"),
    ]:
        session.add(
            StorageFile(
                mesa_id=mesa.id,
                bucket=CAMPAIGNS_BUCKET,
                relative_path=path,
                resource_type=StorageResourceType.CHARACTER_SHEET,
                resource_id=sheet_id,
                content_type="application/json",
                contract=contract,
                contract_version="1.0.0",
                entity_version=1,
                byte_size=len(raw),
                checksum_sha256=sha256_hex(raw),
                last_validated_at=now,
            )
        )

    await session.flush()
    await log_audit(
        session,
        actor_id=owner.id,
        mesa_id=mesa.id,
        action="character.created",
        resource_type="character_sheet",
        resource_id=sheet_id,
    )
    return sheet


async def update_character_data(
    session: AsyncSession,
    storage: StorageService,
    *,
    sheet: CharacterSheet,
    mesa: Mesa,
    template: SheetTemplate,
    user: User,
    values: dict[str, Any],
) -> CharacterSheet:
    new_version = sheet.version + 1
    version_path = f"{mesa.id}/characters/{sheet.id}/versions/v{new_version}.json"

    envelope = build_envelope(
        contract="rpg.character-sheet",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=sheet.id,
        entity_version=new_version,
        payload={
            "template_id": str(sheet.template_id),
            "template_entity_version": template.version,
            "values": values,
        },
    )
    validate_envelope(envelope)

    raw = await storage.put_json(CAMPAIGNS_BUCKET, version_path, envelope)
    await storage.put_json(CAMPAIGNS_BUCKET, sheet.storage_path, envelope)

    sheet.version = new_version
    session.add(
        CharacterSheetVersion(
            sheet_id=sheet.id,
            mesa_id=mesa.id,
            version=new_version,
            storage_path=version_path,
            checksum_sha256=sha256_hex(raw),
            created_by=user.id,
        )
    )
    await session.flush()
    return sheet
