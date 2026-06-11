"""Document CRUD with contract validation."""

from __future__ import annotations

import uuid
from typing import Any

from rpg_platform.contracts.validator import build_envelope, sha256_hex, validate_envelope
from rpg_platform.db.enums import (
    ContentFormat,
    DocumentType,
    DocumentVisibility,
    StorageResourceType,
)
from rpg_platform.db.models import Document, Mesa, StorageFile, User
from rpg_platform.services.audit import log_audit
from rpg_platform.services.storage import StorageService
from rpg_platform.time_utils import utcnow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

CAMPAIGNS_BUCKET = "campaigns"


def _document_meta_payload(
    *,
    title: str,
    doc_type: DocumentType,
    visibility: DocumentVisibility,
    content_format: ContentFormat,
    created_by: uuid.UUID,
    tags: list[str] | None = None,
    visibility_targets: list[str] | None = None,
    character_sheet_id: str | None = None,
) -> dict[str, Any]:
    return {
        "title": title,
        "type": doc_type.value,
        "tags": tags or [],
        "visibility": visibility.value,
        "visibility_targets": visibility_targets or [],
        "content_format": content_format.value,
        "created_by": str(created_by),
        "character_sheet_id": character_sheet_id,
    }


async def list_documents(
    session: AsyncSession,
    mesa_id: uuid.UUID,
    *,
    q: str | None = None,
) -> list[Document]:
    stmt = select(Document).where(Document.mesa_id == mesa_id, Document.deleted_at.is_(None))
    result = await session.execute(stmt.order_by(Document.updated_at.desc()))
    docs = list(result.scalars().all())
    if q:
        needle = q.lower()
        docs = [d for d in docs if needle in d.title.lower() or any(needle in t.lower() for t in d.tags)]
    return docs


async def create_document(
    session: AsyncSession,
    storage: StorageService,
    *,
    mesa: Mesa,
    user: User,
    title: str,
    doc_type: DocumentType,
    visibility: DocumentVisibility,
    content_format: ContentFormat = ContentFormat.MARKDOWN,
    tags: list[str] | None = None,
    initial_content: str = "",
) -> Document:
    doc_id = uuid.uuid4()
    meta_path = f"{mesa.id}/documents/{doc_id}/meta.json"

    if content_format == ContentFormat.MARKDOWN:
        content_path = f"{mesa.id}/documents/{doc_id}/content.md"
        content_contract = "rpg.document-meta"
    else:
        content_path = f"{mesa.id}/documents/{doc_id}/content.json"
        content_contract = "rpg.structured-document"

    meta_envelope = build_envelope(
        contract="rpg.document-meta",
        contract_version="1.0.0",
        mesa_id=mesa.id,
        resource_id=doc_id,
        entity_version=1,
        payload=_document_meta_payload(
            title=title,
            doc_type=doc_type,
            visibility=visibility,
            content_format=content_format,
            created_by=user.id,
            tags=tags,
        ),
    )
    validate_envelope(meta_envelope)
    meta_raw = await storage.put_json(CAMPAIGNS_BUCKET, meta_path, meta_envelope)

    if content_format == ContentFormat.MARKDOWN:
        content_raw = initial_content.encode("utf-8")
        await storage.put_bytes(CAMPAIGNS_BUCKET, content_path, content_raw, content_type="text/markdown")
        content_checksum = sha256_hex(content_raw)
        content_byte_size = len(content_raw)
    else:
        content_envelope = build_envelope(
            contract="rpg.structured-document",
            contract_version="1.0.0",
            mesa_id=mesa.id,
            resource_id=doc_id,
            entity_version=1,
            payload={
                "title": title,
                "sections": [{"key": "main", "content": initial_content or ""}],
            },
        )
        validate_envelope(content_envelope)
        content_raw = await storage.put_json(CAMPAIGNS_BUCKET, content_path, content_envelope)
        content_checksum = sha256_hex(content_raw)
        content_byte_size = len(content_raw)

    now = utcnow()
    document = Document(
        id=doc_id,
        mesa_id=mesa.id,
        type=doc_type,
        title=title,
        tags=tags or [],
        visibility=visibility,
        content_format=content_format,
        created_by=user.id,
        version=1,
        storage_path=content_path,
        meta_storage_path=meta_path,
        contract=content_contract if content_format == ContentFormat.STRUCTURED_JSON else "rpg.document-meta",
        contract_version="1.0.0",
    )
    session.add(document)
    session.add(
        StorageFile(
            mesa_id=mesa.id,
            bucket=CAMPAIGNS_BUCKET,
            relative_path=meta_path,
            resource_type=StorageResourceType.DOCUMENT,
            resource_id=doc_id,
            content_type="application/json",
            contract="rpg.document-meta",
            contract_version="1.0.0",
            entity_version=1,
            byte_size=len(meta_raw),
            checksum_sha256=sha256_hex(meta_raw),
            last_validated_at=now,
        )
    )
    if content_format == ContentFormat.STRUCTURED_JSON:
        session.add(
            StorageFile(
                mesa_id=mesa.id,
                bucket=CAMPAIGNS_BUCKET,
                relative_path=content_path,
                resource_type=StorageResourceType.DOCUMENT,
                resource_id=doc_id,
                content_type="application/json",
                contract="rpg.structured-document",
                contract_version="1.0.0",
                entity_version=1,
                byte_size=content_byte_size,
                checksum_sha256=content_checksum,
                last_validated_at=now,
            )
        )

    await session.flush()
    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=mesa.id,
        action="document.created",
        resource_type="document",
        resource_id=doc_id,
    )
    return document


async def soft_delete_document(
    session: AsyncSession,
    document: Document,
    user: User,
) -> Document:
    document.deleted_at = utcnow()
    await session.flush()
    await log_audit(
        session,
        actor_id=user.id,
        mesa_id=document.mesa_id,
        action="document.deleted",
        resource_type="document",
        resource_id=document.id,
    )
    return document


async def get_document_content(storage: StorageService, document: Document) -> dict[str, Any]:
    if document.content_format == ContentFormat.MARKDOWN:
        raw = await storage.get_bytes(CAMPAIGNS_BUCKET, document.storage_path)
        return {"format": "markdown", "body": raw.decode("utf-8")}
    return await storage.get_json(CAMPAIGNS_BUCKET, document.storage_path)
