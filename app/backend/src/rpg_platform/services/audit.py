"""Audit event logging."""

from __future__ import annotations

import uuid
from typing import Any

from rpg_platform.db.models import AuditEvent
from sqlalchemy.ext.asyncio import AsyncSession


async def log_audit(
    session: AsyncSession,
    *,
    actor_id: uuid.UUID,
    action: str,
    resource_type: str,
    mesa_id: uuid.UUID | None = None,
    resource_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        mesa_id=mesa_id,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata or {},
    )
    session.add(event)
    await session.flush()
    return event
