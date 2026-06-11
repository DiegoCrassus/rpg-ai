"""Studio Service FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studio_service import __version__
from studio_service.api.errors import register_studio_exception_handlers
from studio_service.api.router import router as studio_router
from studio_service.config import get_settings
from studio_service.middleware.auth import StudioAuthMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.add_middleware(StudioAuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_studio_exception_handlers(app)
    app.include_router(studio_router, prefix="/studio")
    return app


app = create_app()
