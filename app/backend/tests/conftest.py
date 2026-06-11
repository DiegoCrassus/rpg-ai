"""Shared pytest fixtures for RPG backend."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from rpg_platform.api.deps import get_db, get_storage, set_storage_service
from rpg_platform.auth.jwt import create_test_token
from rpg_platform.config import get_settings
from rpg_platform.db import session as db_session_module
from rpg_platform.db.base import Base
from rpg_platform.main import create_app
from rpg_platform.services.storage import StorageService, clear_memory_storage
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite+aiosqlite://"
TEST_JWT_SECRET = "test-jwt-secret-for-local-dev-only"


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")
    get_settings.cache_clear()
    db_session_module.reset_engine()
    clear_memory_storage()
    set_storage_service(StorageService(use_memory=True))


@pytest.fixture
async def engine():
    eng = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db_session_module._engine = eng
    db_session_module._session_factory = async_sessionmaker(eng, expire_on_commit=False)
    yield eng
    await eng.dispose()
    db_session_module.reset_engine()


@pytest.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
        await session.commit()


@pytest.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: StorageService(use_memory=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def auth_header(user_id: uuid.UUID | None = None, email: str = "master@example.com") -> dict[str, str]:
    uid = str(user_id or uuid.uuid4())
    token = create_test_token(uid, email, secret=TEST_JWT_SECRET)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def master_headers() -> dict[str, str]:
    return auth_header(email="master@example.com")


@pytest.fixture
def player_headers() -> dict[str, str]:
    return auth_header(email="player@example.com")
