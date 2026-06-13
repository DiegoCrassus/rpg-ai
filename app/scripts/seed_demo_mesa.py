#!/usr/bin/env python3
"""Seed idempotent local demo D&D 5e mesa for admin user."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "app" / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        sys.exit(f"ERROR: missing {env_path} — run make -C app infra")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


async def _run() -> int:
    _load_dotenv()

    from rpg_platform.api.errors import AppError
    from rpg_platform.config import get_settings
    from rpg_platform.db import session as db_session_module
    from rpg_platform.db.session import get_session_factory
    from rpg_platform.services.demo_mesa_seed import ensure_demo_mesa
    from rpg_platform.services.storage import StorageService

    get_settings.cache_clear()
    db_session_module.reset_engine()

    factory = get_session_factory()
    storage = StorageService()

    try:
        async with factory() as session:
            result = await ensure_demo_mesa(session, storage)
            await session.commit()
    except AppError as exc:
        sys.exit(f"ERROR: {exc.message}")

    verb = "created" if result.created else "verified"
    print(f"OK: demo mesa {verb} — id={result.mesa_id}")
    print(f"    character: {result.character_name}")
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
