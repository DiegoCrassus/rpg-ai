"""Optional Bearer token auth for local Studio API (S7)."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from studio_service.config import get_settings

_UNAUTHORIZED_BODY = {
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Missing or invalid Authorization header",
    }
}


def _is_authorized(request: Request, expected_token: str) -> bool:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return False
    return header[7:].strip() == expected_token


class StudioAuthMiddleware(BaseHTTPMiddleware):
    """Require ``Authorization: Bearer <token>`` when ``STUDIO_AUTH_TOKEN`` is set."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        settings = get_settings()
        token = settings.auth_token
        if not token or not request.url.path.startswith("/studio"):
            return await call_next(request)
        if _is_authorized(request, token):
            return await call_next(request)
        return JSONResponse(status_code=401, content=_UNAUTHORIZED_BODY)
