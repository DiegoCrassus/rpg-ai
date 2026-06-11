"""Health check routes."""

from fastapi import APIRouter
from rpg_platform.api.deps import DbSession
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: DbSession) -> dict:
    try:
        await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}
