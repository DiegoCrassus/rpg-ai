"""Sheet import agent runner — mockable for tests."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import Any

from rpg_platform.agents.sheet_import.models import (
    FieldConfidence,
    ImportProposal,
    TemplateFieldProposal,
    TemplateProposal,
)
from rpg_platform.db.enums import ImportJobStatus
from rpg_platform.db.models import SheetImportJob
from rpg_platform.services.sheet_import_jobs import apply_proposal_to_job
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

ProposalBuilder = Callable[[uuid.UUID], dict[str, Any]]


def default_mock_proposal(job_id: uuid.UUID) -> dict[str, Any]:
    proposal = ImportProposal(
        job_id=job_id,
        detected_system="dnd5e_2024",
        detection_confidence=0.85,
        source_pages=1,
        template_proposal=TemplateProposal(
            name="Imported Sheet",
            slug="imported-sheet",
            description="Mock import proposal",
            fields=[
                TemplateFieldProposal(
                    key="character_name",
                    type="text",
                    label="Character Name",
                    required=True,
                    order=0,
                ),
                TemplateFieldProposal(
                    key="level",
                    type="number",
                    label="Level",
                    order=1,
                ),
            ],
        ),
        field_confidence=[
            FieldConfidence(key="character_name", confidence=0.9),
            FieldConfidence(key="level", confidence=0.7),
        ],
        warnings=[],
        requires_review=True,
    )
    return proposal.to_contract_dict()


async def run_import_job(
    session: AsyncSession,
    job_id: uuid.UUID,
    *,
    proposal_builder: ProposalBuilder | None = None,
) -> None:
    """Process import job — uses mock proposal unless real agent configured."""
    job = await session.get(SheetImportJob, job_id)
    if job is None:
        return

    job.status = ImportJobStatus.PROCESSING
    await session.commit()

    try:
        builder = proposal_builder or default_mock_proposal
        proposal = builder(job_id)
        proposal["job_id"] = str(job_id)
        from rpg_platform.contracts.validator import validate_contract_document

        validate_contract_document(proposal, "rpg.sheet-import-proposal")

        job = await session.get(SheetImportJob, job_id)
        if job:
            await apply_proposal_to_job(session, job, proposal)
            await session.commit()
    except Exception as exc:
        logger.exception("Import job %s failed", job_id)
        job = await session.get(SheetImportJob, job_id)
        if job:
            job.status = ImportJobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            )
            await session.commit()


async def run_import_job_with_agent(
    session: AsyncSession,
    job_id: uuid.UUID,
) -> None:
    """Attempt Deep Agent run; fall back to mock on failure."""
    try:
        from rpg_platform.agents.sheet_import.agent import build_proposal_with_agent

        proposal = await build_proposal_with_agent(job_id)
        job = await session.get(SheetImportJob, job_id)
        if job:
            job.status = ImportJobStatus.PROCESSING
            await session.commit()
            await apply_proposal_to_job(session, job, proposal)
            await session.commit()
    except ImportError:
        await run_import_job(session, job_id)
    except Exception:
        await run_import_job(session, job_id)
