"""JWT verification for Supabase Auth tokens."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from rpg_platform.api.errors import AppError
from rpg_platform.config import get_settings

_DECODE_OPTIONS = {"require": ["sub", "exp"]}
_AUDIENCE = "authenticated"


@dataclass
class TokenClaims:
    sub: str
    email: str
    raw: dict[str, Any]


@lru_cache(maxsize=4)
def _jwks_client(supabase_url: str) -> PyJWKClient:
    base = supabase_url.rstrip("/")
    return PyJWKClient(f"{base}/auth/v1/.well-known/jwks.json", cache_keys=True)


def _claims_from_payload(payload: dict[str, Any]) -> TokenClaims:
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    if not email:
        raise AppError("auth_missing_email", "Token missing email claim", 401)
    return TokenClaims(sub=str(payload["sub"]), email=str(email).lower(), raw=payload)


def decode_jwt(token: str) -> TokenClaims:
    """Verify Supabase access tokens (HS256 legacy or ES256 via JWKS)."""
    settings = get_settings()
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AppError("auth_invalid_token", "Invalid or expired token", 401) from exc

    alg = header.get("alg", "HS256")

    try:
        if alg == "HS256":
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=_AUDIENCE,
                options=_DECODE_OPTIONS,
            )
        elif alg == "ES256":
            signing_key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience=_AUDIENCE,
                options=_DECODE_OPTIONS,
            )
        else:
            raise AppError("auth_invalid_token", f"Unsupported JWT algorithm: {alg}", 401)
    except AppError:
        raise
    except jwt.PyJWTError as exc:
        raise AppError("auth_invalid_token", "Invalid or expired token", 401) from exc

    return _claims_from_payload(payload)


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
            "aud": _AUDIENCE,
            "role": "authenticated",
            "exp": int(time.time()) + 3600,
        },
        secret or settings.supabase_jwt_secret,
        algorithm="HS256",
    )
