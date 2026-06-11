"""Pytest fixtures for Studio Service API."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[3]
STUDIO_SRC = REPO_ROOT / "studio/backend/src"

for entry in (str(REPO_ROOT), str(STUDIO_SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

os.environ.setdefault("STUDIO_REPO_ROOT", str(REPO_ROOT))

from studio_service.config import get_settings  # noqa: E402
from studio_service.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _studio_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STUDIO_REPO_ROOT", str(REPO_ROOT))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
