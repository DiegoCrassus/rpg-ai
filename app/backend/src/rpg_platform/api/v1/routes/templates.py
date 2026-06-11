"""Sheet template routes."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field
from rpg_platform.api.deps import CurrentUser, DbSession, StorageDep
from rpg_platform.api.errors import AppError
from rpg_platform.db.models import SheetTemplate
from rpg_platform.policies.mesa import get_mesa_or_404, require_master, require_member
from rpg_platform.services.templates import (
    get_template_schema,
    list_template_versions,
    list_templates,
)

router = APIRouter(prefix="/mesas/{mesa_id}/templates", tags=["templates"])


class TemplateResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    status: str
    version: int
    is_seed: bool


class CreateTemplateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=80)
    description: str | None = None
    fields: list[dict[str, Any]]


def _template_response(t: SheetTemplate) -> TemplateResponse:
    return TemplateResponse(
        id=str(t.id),
        name=t.name,
        slug=t.slug,
        description=t.description,
        status=t.status.value,
        version=t.version,
        is_seed=t.is_seed,
    )


@router.get("", response_model=list[TemplateResponse])
async def get_templates(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> list[TemplateResponse]:
    await require_member(session, mesa_id, user)
    templates = await list_templates(session, mesa_id)
    return [_template_response(t) for t in templates]


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    mesa_id: uuid.UUID,
    body: CreateTemplateRequest,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> TemplateResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    from rpg_platform.contracts.validator import build_envelope, sha256_hex, validate_envelope
    from rpg_platform.db.enums import StorageResourceType, TemplateStatus
    from rpg_platform.db.models import SheetTemplateVersion, StorageFile
    from rpg_platform.services.sheet_import_jobs import CAMPAIGNS_BUCKET
    from rpg_platform.time_utils import utcnow

    template_id = uuid.uuid4()
    storage_path = f"{mesa.id}/templates/{template_id}/schema.json"
    envelope = build_envelope(
        contract="rpg.sheet-template",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=template_id,
        entity_version=1,
        payload={
            "name": body.name,
            "slug": body.slug,
            "description": body.description,
            "is_seed": False,
            "fields": body.fields,
        },
    )
    validate_envelope(envelope)
    raw = await storage.put_json(CAMPAIGNS_BUCKET, storage_path, envelope)
    now = utcnow()
    template = SheetTemplate(
        id=template_id,
        mesa_id=mesa.id,
        name=body.name,
        slug=body.slug,
        description=body.description,
        status=TemplateStatus.ACTIVE,
        version=1,
        storage_path=storage_path,
    )
    session.add(template)
    session.add(
        SheetTemplateVersion(
            template_id=template_id,
            mesa_id=mesa.id,
            version=1,
            storage_path=storage_path,
            checksum_sha256=sha256_hex(raw),
            created_by=user.id,
        )
    )
    session.add(
        StorageFile(
            mesa_id=mesa.id,
            bucket=CAMPAIGNS_BUCKET,
            relative_path=storage_path,
            resource_type=StorageResourceType.SHEET_TEMPLATE,
            resource_id=template_id,
            content_type="application/json",
            contract="rpg.sheet-template",
            contract_version="1.0.0",
            entity_version=1,
            byte_size=len(raw),
            checksum_sha256=sha256_hex(raw),
            last_validated_at=now,
        )
    )
    await session.flush()
    return _template_response(template)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    mesa_id: uuid.UUID,
    template_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> TemplateResponse:
    await require_member(session, mesa_id, user)
    template = await session.get(SheetTemplate, template_id)
    if template is None or template.mesa_id != mesa_id:
        raise AppError("template_not_found", "Template not found", 404)
    return _template_response(template)


@router.patch("/{template_id}", response_model=TemplateResponse)
async def patch_template(
    mesa_id: uuid.UUID,
    template_id: uuid.UUID,
    body: CreateTemplateRequest,
    user: CurrentUser,
    session: DbSession,
) -> TemplateResponse:
    await require_master(session, mesa_id, user)
    template = await session.get(SheetTemplate, template_id)
    if template is None or template.mesa_id != mesa_id:
        raise AppError("template_not_found", "Template not found", 404)
    template.name = body.name
    template.slug = body.slug
    template.description = body.description
    await session.flush()
    return _template_response(template)


@router.get("/{template_id}/schema")
async def get_schema(
    mesa_id: uuid.UUID,
    template_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    await require_member(session, mesa_id, user)
    template = await session.get(SheetTemplate, template_id)
    if template is None or template.mesa_id != mesa_id:
        raise AppError("template_not_found", "Template not found", 404)
    return await get_template_schema(storage, template)


@router.get("/{template_id}/versions")
async def get_versions(
    mesa_id: uuid.UUID,
    template_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> list[dict]:
    await require_member(session, mesa_id, user)
    versions = await list_template_versions(session, template_id)
    return [
        {
            "id": str(v.id),
            "version": v.version,
            "storage_path": v.storage_path,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]
