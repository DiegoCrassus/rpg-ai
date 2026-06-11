"""Document routes."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from rpg_platform.api.deps import CurrentUser, DbSession, StorageDep
from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import ContentFormat, DocumentType, DocumentVisibility
from rpg_platform.db.models import Document
from rpg_platform.policies.document import can_read_document, filter_visible_documents
from rpg_platform.policies.mesa import get_mesa_or_404, require_master, require_member
from rpg_platform.services.documents import (
    create_document,
    get_document_content,
    list_documents,
    soft_delete_document,
)

router = APIRouter(prefix="/mesas/{mesa_id}/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: str
    title: str
    type: str
    visibility: str
    tags: list[str]
    version: int
    content_format: str


class CreateDocumentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: DocumentType
    visibility: DocumentVisibility
    content_format: ContentFormat = ContentFormat.MARKDOWN
    tags: list[str] = Field(default_factory=list)
    initial_content: str = ""


class UpdateDocumentRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    visibility: DocumentVisibility | None = None
    tags: list[str] | None = None


class ContentUpdateRequest(BaseModel):
    content: str | dict[str, Any]


def _doc_response(d: Document) -> DocumentResponse:
    return DocumentResponse(
        id=str(d.id),
        title=d.title,
        type=d.type.value,
        visibility=d.visibility.value,
        tags=d.tags if isinstance(d.tags, list) else [],
        version=d.version,
        content_format=d.content_format.value,
    )


async def _load_document(session, mesa_id, doc_id) -> Document:
    doc = await session.get(Document, doc_id)
    if doc is None or doc.mesa_id != mesa_id or doc.deleted_at is not None:
        raise AppError("document_not_found", "Document not found", 404)
    return doc


@router.get("", response_model=list[DocumentResponse])
async def get_documents(
    mesa_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    q: str | None = Query(default=None),
) -> list[DocumentResponse]:
    participant = await require_member(session, mesa_id, user)
    docs = await list_documents(session, mesa_id, q=q)
    visible = await filter_visible_documents(session, docs, user, participant)
    return [_doc_response(d) for d in visible]


@router.get("/search", response_model=list[DocumentResponse])
async def search_documents(
    mesa_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    q: str = Query(min_length=1),
) -> list[DocumentResponse]:
    return await get_documents(mesa_id, user, session, q=q)


@router.post("", response_model=DocumentResponse, status_code=201)
async def post_document(
    mesa_id: uuid.UUID,
    body: CreateDocumentRequest,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> DocumentResponse:
    await require_master(session, mesa_id, user)
    mesa = await get_mesa_or_404(session, mesa_id)
    doc = await create_document(
        session,
        storage,
        mesa=mesa,
        user=user,
        title=body.title,
        doc_type=body.type,
        visibility=body.visibility,
        content_format=body.content_format,
        tags=body.tags,
        initial_content=body.initial_content,
    )
    return _doc_response(doc)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    mesa_id: uuid.UUID,
    document_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> DocumentResponse:
    participant = await require_member(session, mesa_id, user)
    doc = await _load_document(session, mesa_id, document_id)
    if not await can_read_document(session, doc, user, participant):
        raise AppError("document_forbidden", "Cannot view this document", 403)
    return _doc_response(doc)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def patch_document(
    mesa_id: uuid.UUID,
    document_id: uuid.UUID,
    body: UpdateDocumentRequest,
    user: CurrentUser,
    session: DbSession,
) -> DocumentResponse:
    await require_master(session, mesa_id, user)
    doc = await _load_document(session, mesa_id, document_id)
    if body.title is not None:
        doc.title = body.title
    if body.visibility is not None:
        doc.visibility = body.visibility
    if body.tags is not None:
        doc.tags = body.tags
    await session.flush()
    return _doc_response(doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    mesa_id: uuid.UUID,
    document_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> None:
    await require_master(session, mesa_id, user)
    doc = await _load_document(session, mesa_id, document_id)
    await soft_delete_document(session, doc, user)


@router.get("/{document_id}/content")
async def get_content(
    mesa_id: uuid.UUID,
    document_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    participant = await require_member(session, mesa_id, user)
    doc = await _load_document(session, mesa_id, document_id)
    if not await can_read_document(session, doc, user, participant):
        raise AppError("document_forbidden", "Cannot view this document", 403)
    return await get_document_content(storage, doc)


@router.put("/{document_id}/content")
async def put_content(
    mesa_id: uuid.UUID,
    document_id: uuid.UUID,
    body: ContentUpdateRequest,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    await require_master(session, mesa_id, user)
    doc = await _load_document(session, mesa_id, document_id)
    from rpg_platform.contracts.validator import build_envelope, validate_envelope
    from rpg_platform.db.enums import ContentFormat

    if doc.content_format == ContentFormat.MARKDOWN:
        body_text = body.content if isinstance(body.content, str) else str(body.content)
        await storage.put_bytes("campaigns", doc.storage_path, body_text.encode("utf-8"), content_type="text/markdown")
    else:
        payload = body.content if isinstance(body.content, dict) else {"title": doc.title, "sections": [{"key": "main", "content": str(body.content)}]}
        envelope = build_envelope(
            contract="rpg.structured-document",
            contract_version=doc.contract_version,
            mesa_id=mesa_id,
            resource_id=doc.id,
            entity_version=doc.version + 1,
            payload=payload,
        )
        validate_envelope(envelope)
        await storage.put_json("campaigns", doc.storage_path, envelope)
    doc.version += 1
    await session.flush()
    return {"version": doc.version}
