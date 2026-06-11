from __future__ import annotations

from fastapi import APIRouter

from studio_service.api.routes import (
    canvas,
    config,
    dashboard,
    engine,
    evidence,
    health,
    integrations,
    metadata,
    obs,
    proposals,
    readiness,
    registry,
    session,
    validation_suite,
)

router = APIRouter()
router.include_router(health.router)
router.include_router(readiness.router)
router.include_router(session.router)
router.include_router(engine.router)
router.include_router(dashboard.router)
router.include_router(canvas.router)
router.include_router(obs.router)
router.include_router(proposals.router)
router.include_router(config.router)
router.include_router(registry.router)
router.include_router(validation_suite.router)
router.include_router(integrations.router)
router.include_router(evidence.router)
router.include_router(metadata.router)
