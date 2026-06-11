"""Studio API error envelope (ADR-008)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse


class StudioApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        body: dict[str, Any] = {"error": {"code": code, "message": message}}
        if details is not None:
            body["error"]["details"] = details
        self.body = body
        super().__init__(message)


def register_studio_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StudioApiError)
    async def _handle_studio_api_error(_request, exc: StudioApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.body)
