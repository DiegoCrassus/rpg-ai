"""API v1 router aggregation."""

from fastapi import APIRouter
from rpg_platform.api.v1.routes import (
    admin,
    auth,
    characters,
    documents,
    health,
    import_routes,
    mesas,
    participants,
    templates,
    users,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(mesas.router)
api_router.include_router(import_routes.router)
api_router.include_router(participants.router)
api_router.include_router(templates.router)
api_router.include_router(characters.router)
api_router.include_router(documents.router)
api_router.include_router(admin.router)
