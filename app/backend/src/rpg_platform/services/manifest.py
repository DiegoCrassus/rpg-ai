"""Campaign manifest regeneration."""

from __future__ import annotations

from rpg_platform.contracts.validator import build_envelope, sha256_hex, validate_envelope
from rpg_platform.db.enums import StorageResourceType, TemplateStatus
from rpg_platform.db.models import (
    CampaignAsset,
    CharacterSheet,
    Document,
    Mesa,
    SheetTemplate,
    StorageFile,
)
from rpg_platform.services.storage import StorageService
from rpg_platform.time_utils import utcnow
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

CAMPAIGNS_BUCKET = "campaigns"


async def regenerate_manifest(
    session: AsyncSession,
    storage: StorageService,
    mesa: Mesa,
) -> dict:
    template_count = (
        await session.execute(
            select(func.count())
            .select_from(SheetTemplate)
            .where(SheetTemplate.mesa_id == mesa.id, SheetTemplate.status == TemplateStatus.ACTIVE)
        )
    ).scalar_one()

    character_count = (
        await session.execute(
            select(func.count()).select_from(CharacterSheet).where(CharacterSheet.mesa_id == mesa.id)
        )
    ).scalar_one()

    document_count = (
        await session.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.mesa_id == mesa.id, Document.deleted_at.is_(None))
        )
    ).scalar_one()

    asset_count = (
        await session.execute(
            select(func.count()).select_from(CampaignAsset).where(CampaignAsset.mesa_id == mesa.id)
        )
    ).scalar_one()

    now = utcnow()
    payload = {
        "mesa_id": str(mesa.id),
        "mesa_name": mesa.name,
        "rpg_system": mesa.rpg_system,
        "entity_version": 1,
        "counts": {
            "templates": int(template_count),
            "characters": int(character_count),
            "documents": int(document_count),
            "assets": int(asset_count),
        },
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }

    envelope = build_envelope(
        contract="rpg.campaign-manifest",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=mesa.id,
        entity_version=1,
        payload=payload,
    )
    validate_envelope(envelope)

    raw = await storage.put_json(CAMPAIGNS_BUCKET, mesa.manifest_storage_path, envelope)
    checksum = sha256_hex(raw)

    existing = (
        await session.execute(
            select(StorageFile).where(
                StorageFile.bucket == CAMPAIGNS_BUCKET,
                StorageFile.relative_path == mesa.manifest_storage_path,
            )
        )
    ).scalar_one_or_none()

    validated_at = utcnow()
    if existing:
        existing.byte_size = len(raw)
        existing.checksum_sha256 = checksum
        existing.last_validated_at = validated_at
    else:
        session.add(
            StorageFile(
                mesa_id=mesa.id,
                bucket=CAMPAIGNS_BUCKET,
                relative_path=mesa.manifest_storage_path,
                resource_type=StorageResourceType.MANIFEST,
                resource_id=mesa.id,
                content_type="application/json",
                contract="rpg.campaign-manifest",
                contract_version="1.0.0",
                entity_version=1,
                byte_size=len(raw),
                checksum_sha256=checksum,
                last_validated_at=validated_at,
            )
        )
    await session.flush()
    return envelope
