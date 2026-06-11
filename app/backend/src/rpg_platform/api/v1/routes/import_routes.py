"""Sheet import routes."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, UploadFile
from pydantic import BaseModel
from rpg_platform.agents.sheet_import.runner import run_import_job
from rpg_platform.api.deps import CurrentUser, DbSession, StorageDep
from rpg_platform.api.errors import AppError
from rpg_platform.db.session import get_session_factory
from rpg_platform.policies.mesa import get_mesa_or_404, require_master
from rpg_platform.services.sheet_import_jobs import (
    approve_import,
    enqueue_import,
    get_latest_job,
    reject_import,
    seed_dnd5e_template,
)

router = APIRouter(prefix="/mesas/{mesa_id}/import", tags=["import"])

MIME_EXT = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}


class ImportJobResponse(BaseModel):
    id: str
    status: str
    source_storage_path: str
    source_mime: str
    detected_system: str | None
    proposal: dict[str, Any] | None
    error_message: str | None


def _job_response(job) -> ImportJobResponse:
    return ImportJobResponse(
        id=str(job.id),
        status=job.status.value,
        source_storage_path=job.source_storage_path,
        source_mime=job.source_mime,
        detected_system=job.detected_system,
        proposal=job.proposal,
        error_message=job.error_message,
    )


async def _background_run_job(job_id: uuid.UUID) -> None:
    factory = get_session_factory()
    async with factory() as session:
        await run_import_job(session, job_id)
        await session.commit()


@router.post("", response_model=ImportJobResponse, status_code=202)
async def start_import(
    mesa_id: uuid.UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> ImportJobResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    mime = file.content_type or "application/octet-stream"
    ext = MIME_EXT.get(mime)
    if ext is None:
        raise AppError("import_invalid_mime", "Supported: PDF, PNG, JPEG, WebP", 422)
    data = await file.read()
    job = await enqueue_import(session, storage, mesa=mesa, user=user, file_bytes=data, mime_type=mime, ext=ext)
    await session.commit()
    background_tasks.add_task(_background_run_job, job.id)
    return _job_response(job)


@router.get("", response_model=ImportJobResponse)
async def get_import(mesa_id: uuid.UUID, user: CurrentUser, session: DbSession) -> ImportJobResponse:
    await require_master(session, mesa_id, user)
    job = await get_latest_job(session, mesa_id)
    if job is None:
        raise AppError("import_not_found", "No import job for this Mesa", 404)
    return _job_response(job)


class ProposalPatch(BaseModel):
    proposal: dict[str, Any]


@router.patch("/proposal", response_model=ImportJobResponse)
async def patch_proposal(
    mesa_id: uuid.UUID,
    body: ProposalPatch,
    user: CurrentUser,
    session: DbSession,
) -> ImportJobResponse:
    await require_master(session, mesa_id, user)
    from rpg_platform.db.enums import ImportJobStatus
    from rpg_platform.services.sheet_import_jobs import apply_proposal_to_job

    job = await get_latest_job(session, mesa_id)
    if job is None or job.status != ImportJobStatus.PROPOSED:
        raise AppError("import_not_proposed", "Import is not in proposed state", 409)
    job = await apply_proposal_to_job(session, job, body.proposal)
    return _job_response(job)


@router.post("/approve")
async def approve_import_route(
    mesa_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    job = await get_latest_job(session, mesa_id)
    if job is None:
        raise AppError("import_not_found", "No import job", 404)
    template = await approve_import(session, storage, job=job, mesa=mesa, user=user)
    return {"template_id": str(template.id), "mesa_status": mesa.status.value}


@router.post("/reject", response_model=ImportJobResponse)
async def reject_import_route(
    mesa_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> ImportJobResponse:
    await require_master(session, mesa_id, user)
    job = await get_latest_job(session, mesa_id)
    if job is None:
        raise AppError("import_not_found", "No import job", 404)
    job = await reject_import(session, job, user)
    return _job_response(job)


@router.post("/seed")
async def seed_import(
    mesa_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    template = await seed_dnd5e_template(session, storage, mesa=mesa, user=user)
    return {"template_id": str(template.id), "mesa_status": mesa.status.value}
