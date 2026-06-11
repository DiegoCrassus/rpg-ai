"""Sheet import job orchestration."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from rpg_platform.api.errors import AppError
from rpg_platform.contracts.validator import (
    build_envelope,
    sha256_hex,
    validate_contract_document,
    validate_envelope,
)
from rpg_platform.db.enums import ImportJobStatus, MesaStatus, StorageResourceType, TemplateStatus
from rpg_platform.db.models import (
    Mesa,
    SheetImportJob,
    SheetTemplate,
    SheetTemplateVersion,
    StorageFile,
    User,
)
from rpg_platform.services.audit import log_audit
from rpg_platform.services.manifest import CAMPAIGNS_BUCKET, regenerate_manifest
from rpg_platform.services.storage import StorageService
from rpg_platform.time_utils import utcnow
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

SEEDS_DIR = Path(__file__).resolve().parents[4] / "shared" / "seeds" / "dnd5e"


async def count_recent_imports(session: AsyncSession, mesa_id: uuid.UUID) -> int:
    since = utcnow().replace(microsecond=0)
    since = since.replace(hour=since.hour - 1 if since.hour else 23)
    result = await session.execute(
        select(func.count())
        .select_from(SheetImportJob)
        .where(SheetImportJob.mesa_id == mesa_id, SheetImportJob.created_at >= since)
    )
    return int(result.scalar_one())


async def get_latest_job(session: AsyncSession, mesa_id: uuid.UUID) -> SheetImportJob | None:
    result = await session.execute(
        select(SheetImportJob)
        .where(SheetImportJob.mesa_id == mesa_id)
        .order_by(SheetImportJob.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def enqueue_import(
    session: AsyncSession,
    storage: StorageService,
    *,
    mesa: Mesa,
    user: User,
    file_bytes: bytes,
    mime_type: str,
    ext: str,
) -> SheetImportJob:
    count = await count_recent_imports(session, mesa.id)
    if count >= 5:
        raise AppError("import_rate_limited", "Maximum 5 imports per hour per Mesa", 429)

    path = f"{mesa.id}/import/source.{ext}"
    await storage.put_bytes(CAMPAIGNS_BUCKET, path, file_bytes, content_type=mime_type)

    job = SheetImportJob(
        mesa_id=mesa.id,
        created_by=user.id,
        status=ImportJobStatus.PENDING,
        source_storage_path=path,
        source_mime=mime_type,
    )
    session.add(job)
    await session.flush()
    return job


async def apply_proposal_to_job(
    session: AsyncSession,
    job: SheetImportJob,
    proposal: dict[str, Any],
) -> SheetImportJob:
    validate_contract_document(proposal, "rpg.sheet-import-proposal")
    job.proposal = proposal
    job.detected_system = proposal.get("detected_system")
    job.status = ImportJobStatus.PROPOSED
    job.completed_at = utcnow()
    await session.flush()
    return job


async def approve_import(
    session: AsyncSession,
    storage: StorageService,
    *,
    job: SheetImportJob,
    mesa: Mesa,
    user: User,
) -> SheetTemplate:
    if job.status != ImportJobStatus.PROPOSED or not job.proposal:
        raise AppError("import_not_proposed", "No proposed import to approve", 409)

    proposal = job.proposal
    template_proposal = proposal["template_proposal"]
    template_id = uuid.uuid4()
    storage_path = f"{mesa.id}/templates/{template_id}/schema.json"

    payload = {
        "name": template_proposal["name"],
        "slug": template_proposal["slug"],
        "is_seed": False,
        "fields": template_proposal["fields"],
    }
    if template_proposal.get("description"):
        payload["description"] = template_proposal["description"]
    envelope = build_envelope(
        contract="rpg.sheet-template",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=template_id,
        entity_version=1,
        payload=payload,
    )
    validate_envelope(envelope)

    raw = await storage.put_json(CAMPAIGNS_BUCKET, storage_path, envelope)
    checksum = sha256_hex(raw)
    now = utcnow()

    template = SheetTemplate(
        id=template_id,
        mesa_id=mesa.id,
        name=template_proposal["name"],
        slug=template_proposal["slug"],
        description=template_proposal.get("description"),
        status=TemplateStatus.ACTIVE,
        is_seed=False,
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
            checksum_sha256=checksum,
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
            checksum_sha256=checksum,
            last_validated_at=now,
        )
    )

    job.status = ImportJobStatus.APPROVED
    job.result_template_id = template_id
    job.completed_at = now
    mesa.status = MesaStatus.ACTIVE

    await session.flush()
    await regenerate_manifest(session, storage, mesa)
    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=mesa.id,
        action="import.approved",
        resource_type="sheet_import_job",
        resource_id=job.id,
    )
    return template


async def reject_import(session: AsyncSession, job: SheetImportJob, user: User) -> SheetImportJob:
    job.status = ImportJobStatus.REJECTED
    job.completed_at = utcnow()
    await session.flush()
    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=job.mesa_id,
        action="import.rejected",
        resource_type="sheet_import_job",
        resource_id=job.id,
    )
    return job


async def seed_dnd5e_template(
    session: AsyncSession,
    storage: StorageService,
    *,
    mesa: Mesa,
    user: User,
) -> SheetTemplate:
    seed_path = SEEDS_DIR / "schema.json"
    if not seed_path.exists():
        raise AppError("seed_missing", "D&D 5e seed not found", 500)

    with seed_path.open(encoding="utf-8") as handle:
        seed_envelope = json.load(handle)

    template_id = uuid.uuid4()
    storage_path = f"{mesa.id}/templates/{template_id}/schema.json"

    payload = seed_envelope["payload"]
    envelope = build_envelope(
        contract="rpg.sheet-template",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=template_id,
        entity_version=1,
        payload=payload,
    )
    validate_envelope(envelope)

    raw = await storage.put_json(CAMPAIGNS_BUCKET, storage_path, envelope)
    checksum = sha256_hex(raw)
    now = utcnow()

    template = SheetTemplate(
        id=template_id,
        mesa_id=mesa.id,
        name=payload["name"],
        slug=payload["slug"],
        description=payload.get("description"),
        status=TemplateStatus.ACTIVE,
        is_seed=True,
        seed_key=payload.get("seed_key", "dnd5e"),
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
            checksum_sha256=checksum,
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
            checksum_sha256=checksum,
            last_validated_at=now,
        )
    )

    mesa.status = MesaStatus.ACTIVE
    await session.flush()
    await regenerate_manifest(session, storage, mesa)
    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=mesa.id,
        action="import.seed_applied",
        resource_type="sheet_template",
        resource_id=template_id,
    )
    return template
