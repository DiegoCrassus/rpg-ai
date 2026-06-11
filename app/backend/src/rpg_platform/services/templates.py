"""Sheet template service helpers."""

from __future__ import annotations

import uuid

from rpg_platform.db.enums import TemplateStatus
from rpg_platform.db.models import SheetTemplate, SheetTemplateVersion
from rpg_platform.services.storage import StorageService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

CAMPAIGNS_BUCKET = "campaigns"


async def list_templates(session: AsyncSession, mesa_id: uuid.UUID) -> list[SheetTemplate]:
    result = await session.execute(
        select(SheetTemplate)
        .where(SheetTemplate.mesa_id == mesa_id, SheetTemplate.status == TemplateStatus.ACTIVE)
        .order_by(SheetTemplate.created_at)
    )
    return list(result.scalars().all())


async def get_template_schema(storage: StorageService, template: SheetTemplate) -> dict:
    return await storage.get_json(CAMPAIGNS_BUCKET, template.storage_path)


async def list_template_versions(
    session: AsyncSession, template_id: uuid.UUID
) -> list[SheetTemplateVersion]:
    result = await session.execute(
        select(SheetTemplateVersion)
        .where(SheetTemplateVersion.template_id == template_id)
        .order_by(SheetTemplateVersion.version.desc())
    )
    return list(result.scalars().all())
