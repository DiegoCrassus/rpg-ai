"""User profile sync and updates."""

from __future__ import annotations

import uuid

from rpg_platform.auth.jwt import TokenClaims
from rpg_platform.db.models import User
from rpg_platform.time_utils import utcnow
from sqlalchemy.ext.asyncio import AsyncSession


async def sync_user_from_claims(session: AsyncSession, claims: TokenClaims) -> User:
    user_id = uuid.UUID(claims.sub)
    user = await session.get(User, user_id)
    now = utcnow()
    display = claims.raw.get("user_metadata", {}).get("full_name") or claims.email.split("@")[0]

    if user is None:
        user = User(
            id=user_id,
            email=claims.email,
            display_name=display[:120],
            last_login_at=now,
        )
        session.add(user)
    else:
        user.email = claims.email
        user.last_login_at = now
        if not user.display_name:
            user.display_name = display[:120]

    await session.flush()
    return user
