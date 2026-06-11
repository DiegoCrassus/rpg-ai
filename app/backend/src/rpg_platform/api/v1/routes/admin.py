"""Admin routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel
from rpg_platform.api.deps import CurrentUser, DbSession
from rpg_platform.api.errors import AppError
from rpg_platform.db.enums import UserStatus
from rpg_platform.db.models import AuditEvent, Mesa, User
from sqlalchemy import select

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: User) -> None:
    if not user.is_admin:
        raise AppError("admin_required", "Admin access required", 403)


class AdminUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    status: str
    is_admin: bool
    master_mesa_count: int


class StatusUpdateRequest(BaseModel):
    status: UserStatus


@router.get("/users", response_model=list[AdminUserResponse])
async def admin_list_users(user: CurrentUser, session: DbSession) -> list[AdminUserResponse]:
    require_admin(user)
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return [
        AdminUserResponse(
            id=str(u.id),
            email=u.email,
            display_name=u.display_name,
            status=u.status.value,
            is_admin=u.is_admin,
            master_mesa_count=u.master_mesa_count,
        )
        for u in result.scalars().all()
    ]


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
async def admin_update_user_status(
    user_id: uuid.UUID,
    body: StatusUpdateRequest,
    user: CurrentUser,
    session: DbSession,
) -> AdminUserResponse:
    require_admin(user)
    target = await session.get(User, user_id)
    if target is None:
        raise AppError("user_not_found", "User not found", 404)
    target.status = body.status
    await session.flush()
    return AdminUserResponse(
        id=str(target.id),
        email=target.email,
        display_name=target.display_name,
        status=target.status.value,
        is_admin=target.is_admin,
        master_mesa_count=target.master_mesa_count,
    )


@router.get("/mesas")
async def admin_list_mesas(user: CurrentUser, session: DbSession) -> list[dict]:
    require_admin(user)
    result = await session.execute(select(Mesa).order_by(Mesa.created_at.desc()))
    return [
        {
            "id": str(m.id),
            "name": m.name,
            "status": m.status.value,
            "master_id": str(m.master_id),
            "rpg_system": m.rpg_system,
        }
        for m in result.scalars().all()
    ]


@router.get("/audit-events")
async def admin_audit_events(
    user: CurrentUser,
    session: DbSession,
    mesa_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, le=200),
) -> list[dict]:
    require_admin(user)
    stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
    if mesa_id:
        stmt = stmt.where(AuditEvent.mesa_id == mesa_id)
    result = await session.execute(stmt)
    return [
        {
            "id": e.id,
            "mesa_id": str(e.mesa_id) if e.mesa_id else None,
            "actor_id": str(e.actor_id),
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": str(e.resource_id) if e.resource_id else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]
