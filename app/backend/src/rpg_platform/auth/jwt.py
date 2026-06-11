"""JWT verification for Supabase Auth tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt
from rpg_platform.api.errors import AppError
from rpg_platform.config import get_settings


@dataclass
class TokenClaims:
    sub: str
    email: str
    raw: dict[str, Any]


def decode_jwt(token: str) -> TokenClaims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise AppError("auth_invalid_token", "Invalid or expired token", 401) from exc

    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    if not email:
        raise AppError("auth_missing_email", "Token missing email claim", 401)

    return TokenClaims(sub=str(payload["sub"]), email=str(email).lower(), raw=payload)


def create_test_token(
    user_id: str,
    email: str,
    *,
    secret: str | None = None,
) -> str:
    """Issue HS256 token for tests."""
    import time

    settings = get_settings()
    return jwt.encode(
        {
            "sub": user_id,
            "email": email,
            "aud": "authenticated",
            "role": "authenticated",
            "exp": int(time.time()) + 3600,
        },
        secret or settings.supabase_jwt_secret,
        algorithm="HS256",
    )
