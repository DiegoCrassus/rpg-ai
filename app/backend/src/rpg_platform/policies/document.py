"""Document visibility policies."""

from __future__ import annotations

from rpg_platform.db.enums import DocumentVisibility, ParticipantRole
from rpg_platform.db.models import Document, DocumentPermission, MesaParticipant, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def can_read_document(
    session: AsyncSession,
    document: Document,
    user: User,
    participant: MesaParticipant | None,
) -> bool:
    if user.is_admin:
        return True
    if participant is None:
        return False
    if participant.role == ParticipantRole.MASTER:
        return True

    visibility = document.visibility
    if visibility == DocumentVisibility.MASTER_ONLY:
        return False
    if visibility == DocumentVisibility.ALL_PLAYERS:
        return True
    if visibility == DocumentVisibility.OWNER_PRIVATE:
        return document.created_by == user.id
    if visibility == DocumentVisibility.SPECIFIC_PLAYERS:
        result = await session.execute(
            select(DocumentPermission).where(
                DocumentPermission.document_id == document.id,
                DocumentPermission.grantee_id == user.id,
            )
        )
        return result.scalar_one_or_none() is not None
    if visibility == DocumentVisibility.SPECIFIC_CHARACTER:
        result = await session.execute(
            select(DocumentPermission).where(
                DocumentPermission.document_id == document.id,
            )
        )
        perms = result.scalars().all()
        # Player must own linked character sheet
        if document.character_sheet_id:
            from rpg_platform.db.models import CharacterSheet

            sheet = await session.get(CharacterSheet, document.character_sheet_id)
            if sheet and sheet.owner_id == user.id:
                return True
        return any(p.grantee_id == user.id for p in perms)

    return False


async def filter_visible_documents(
    session: AsyncSession,
    documents: list[Document],
    user: User,
    participant: MesaParticipant | None,
) -> list[Document]:
    visible: list[Document] = []
    for doc in documents:
        if await can_read_document(session, doc, user, participant):
            visible.append(doc)
    return visible
