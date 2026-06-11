"""ORM models matching 00001_rpg_platform_schema.sql."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from rpg_platform.db.base import Base
from rpg_platform.db.enums import (
    ContentFormat,
    DocumentType,
    DocumentVisibility,
    ImportJobStatus,
    InviteStatus,
    MesaStatus,
    ParticipantRole,
    ParticipantStatus,
    PermissionGranteeType,
    SheetStatus,
    SheetVisibility,
    StorageResourceType,
    TemplateStatus,
    UserStatus,
)
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

# SQLite-friendly JSON type
JsonType = JSON().with_variant(JSONB, "postgresql")
StringArray = JSON().with_variant(ARRAY(String), "postgresql")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    master_mesa_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    mesas_mastered: Mapped[list[Mesa]] = relationship(back_populates="master")


class Mesa(Base):
    __tablename__ = "mesas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rpg_system: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[MesaStatus] = mapped_column(default=MesaStatus.IMPORTING, nullable=False)
    master_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(
        JsonType,
        nullable=False,
        default=lambda: {
            "players_can_edit_own_sheet": True,
            "players_can_view_other_sheets": False,
            "character_story_requires_approval": False,
            "seed_dnd5e_template": True,
        },
    )
    storage_root: Mapped[str] = mapped_column(Text, nullable=False)
    manifest_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    master: Mapped[User] = relationship(back_populates="mesas_mastered")
    participants: Mapped[list[MesaParticipant]] = relationship(back_populates="mesa")


class MesaParticipant(Base):
    __tablename__ = "mesa_participants"
    __table_args__ = (UniqueConstraint("mesa_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[ParticipantRole] = mapped_column(nullable=False)
    status: Mapped[ParticipantStatus] = mapped_column(
        default=ParticipantStatus.PENDING, nullable=False
    )
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    mesa: Mapped[Mesa] = relationship(back_populates="participants")
    user: Mapped[User] = relationship()


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    status: Mapped[InviteStatus] = mapped_column(default=InviteStatus.PENDING, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SheetTemplate(Base):
    __tablename__ = "sheet_templates"
    __table_args__ = (UniqueConstraint("mesa_id", "slug"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TemplateStatus] = mapped_column(default=TemplateStatus.ACTIVE, nullable=False)
    is_seed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    seed_key: Mapped[str | None] = mapped_column(String(40), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    contract: Mapped[str] = mapped_column(String(64), default="rpg.sheet-template", nullable=False)
    contract_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CharacterSheet(Base):
    __tablename__ = "character_sheets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sheet_templates.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    character_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[SheetStatus] = mapped_column(default=SheetStatus.ACTIVE, nullable=False)
    visibility: Mapped[SheetVisibility] = mapped_column(
        default=SheetVisibility.OWNER_ONLY, nullable=False
    )
    template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_outdated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    meta_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    contract: Mapped[str] = mapped_column(String(64), default="rpg.character-sheet", nullable=False)
    contract_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SheetImportJob(Base):
    __tablename__ = "sheet_import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ImportJobStatus] = mapped_column(default=ImportJobStatus.PENDING, nullable=False)
    source_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_mime: Mapped[str] = mapped_column(String(127), nullable=False)
    detected_system: Mapped[str | None] = mapped_column(String(40), nullable=True)
    proposal: Mapped[dict[str, Any] | None] = mapped_column(JsonType, nullable=True)
    result_template_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sheet_templates.id"), nullable=True
    )
    result_sheet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("character_sheets.id"), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SheetTemplateVersion(Base):
    __tablename__ = "sheet_template_versions"
    __table_args__ = (UniqueConstraint("template_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sheet_templates.id", ondelete="CASCADE")
    )
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CharacterSheetVersion(Base):
    __tablename__ = "character_sheet_versions"
    __table_args__ = (UniqueConstraint("sheet_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("character_sheets.id", ondelete="CASCADE")
    )
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    type: Mapped[DocumentType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    tags: Mapped[list[str]] = mapped_column(StringArray, default=list, nullable=False)
    visibility: Mapped[DocumentVisibility] = mapped_column(nullable=False)
    content_format: Mapped[ContentFormat] = mapped_column(
        default=ContentFormat.MARKDOWN, nullable=False
    )
    character_sheet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("character_sheets.id"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    meta_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    contract: Mapped[str] = mapped_column(String(64), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DocumentPermission(Base):
    __tablename__ = "document_permissions"
    __table_args__ = (UniqueConstraint("document_id", "grantee_type", "grantee_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    grantee_type: Mapped[PermissionGranteeType] = mapped_column(nullable=False)
    grantee_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CampaignAsset(Base):
    __tablename__ = "campaign_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StorageFile(Base):
    __tablename__ = "storage_files"
    __table_args__ = (UniqueConstraint("bucket", "relative_path"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mesa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mesas.id", ondelete="CASCADE"))
    bucket: Mapped[str] = mapped_column(String(64), default="campaigns", nullable=False)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[StorageResourceType] = mapped_column(nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)
    contract: Mapped[str] = mapped_column(String(64), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    last_validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mesa_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("mesas.id"), nullable=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


Index("users_status_idx", User.status)
Index("mesas_master_id_idx", Mesa.master_id)
Index("mesas_status_idx", Mesa.status)
Index("documents_mesa_active_idx", Document.mesa_id, Document.deleted_at)
