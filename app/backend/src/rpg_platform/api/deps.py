"""FastAPI dependencies."""

from __future__ import annotations

import sys
from typing import Annotated

from fastapi import Depends, Header
from rpg_platform.api.errors import AppError
from rpg_platform.auth.jwt import TokenClaims, decode_jwt
from rpg_platform.config import get_settings
from rpg_platform.db.models import User
from rpg_platform.db.session import get_db
from rpg_platform.policies.mesa import get_user_or_404
from rpg_platform.services.storage import StorageService
from rpg_platform.services.users import sync_user_from_claims
from sqlalchemy.ext.asyncio import AsyncSession

_storage_service: StorageService | None = None


def _is_test_runtime() -> bool:
    if "pytest" in sys.modules:
        return True
    return get_settings().app_env.lower() == "test"


def get_storage() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService(use_memory=_is_test_runtime())
    return _storage_service


def set_storage_service(service: StorageService) -> None:
    global _storage_service
    _storage_service = service


def reset_storage_service() -> None:
    global _storage_service
    _storage_service = None


async def get_token_claims(
    authorization: Annotated[str | None, Header()] = None,
) -> TokenClaims:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError("auth_required", "Authorization header required", 401)
    token = authorization.split(" ", 1)[1].strip()
    return decode_jwt(token)


async def get_current_user(
    claims: Annotated[TokenClaims, Depends(get_token_claims)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user = await sync_user_from_claims(session, claims)
    return await get_user_or_404(session, user.id)


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
StorageDep = Annotated[StorageService, Depends(get_storage)]
