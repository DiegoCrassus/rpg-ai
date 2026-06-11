#!/usr/bin/env python3
"""Merge Supabase local status into repo root .env (DATABASE_URL + SUPABASE_*)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
SUPABASE_DIR = ROOT / "app" / "infra" / "supabase"

# supabase status -o env keys -> .env keys
KEY_MAP = {
    "API_URL": "SUPABASE_URL",
    "DB_URL": "DATABASE_URL",
    "ANON_KEY": "SUPABASE_ANON_KEY",
    "SERVICE_ROLE_KEY": "SUPABASE_SERVICE_ROLE_KEY",
    "JWT_SECRET": "SUPABASE_JWT_SECRET",
}


def _find_supabase() -> str:
    home_local = Path.home() / ".local" / "bin" / "supabase"
    if home_local.is_file():
        return str(home_local)
    found = shutil.which("supabase")
    if found:
        return found
    sys.exit("ERROR: supabase CLI not found")


def _parse_status_env() -> dict[str, str]:
    cmd = [_find_supabase(), "status", "-o", "env"]
    proc = subprocess.run(cmd, cwd=SUPABASE_DIR, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        sys.exit(f"ERROR: supabase status failed:\n{proc.stderr or proc.stdout}")

    out: dict[str, str] = {}
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^([A-Z_]+)="?(.*?)"?$', line)
        if not m:
            continue
        out[m.group(1)] = m.group(2).strip('"')
    return out


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _read_env_lines() -> list[str]:
    if not ENV_PATH.is_file():
        return []
    return ENV_PATH.read_text(encoding="utf-8").splitlines()


def _should_sync_database(current: str | None) -> bool:
    if not current:
        return True
    lower = current.lower()
    return "sqlite" in lower or "rpg_op" in lower


def _merge_env(updates: dict[str, str]) -> list[str]:
    lines = _read_env_lines()
    index = {i: line for i, line in enumerate(lines)}
    keys_present: set[str] = set()

    for i, line in enumerate(lines):
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        keys_present.add(key)
        if key not in updates:
            continue
        if key == "DATABASE_URL" and not _should_sync_database(val.strip()):
            continue
        if key.startswith("SUPABASE_") and val.strip():
            continue
        lines[i] = f"{key}={updates[key]}"

    for key, val in updates.items():
        if key in keys_present:
            continue
        if key == "DATABASE_URL" or key.startswith("SUPABASE_"):
            lines.append(f"{key}={val}")

    return lines


def main() -> int:
    status = _parse_status_env()
    updates: dict[str, str] = {}
    for src, dst in KEY_MAP.items():
        if src in status and status[src]:
            value = status[src]
            if dst == "DATABASE_URL":
                value = _normalize_database_url(value)
            updates[dst] = value

    if "DATABASE_URL" not in updates:
        sys.exit("ERROR: DB_URL missing from supabase status")

    if not ENV_PATH.is_file():
        lines = [f"{k}={v}" for k, v in updates.items()]
        ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"OK: created {ENV_PATH} with Supabase local vars")
        return 0

    before = ENV_PATH.read_text(encoding="utf-8")
    lines = _merge_env(updates)
    after = "\n".join(lines) + "\n"
    ENV_PATH.write_text(after, encoding="utf-8")

    if before != after:
        print(f"OK: updated {ENV_PATH} from supabase status")
        for key in updates:
            print(f"  - {key}")
    else:
        print(f"OK: {ENV_PATH} already has Supabase vars")

    _sync_frontend_env(updates)
    return 0


def _sync_frontend_env(updates: dict[str, str]) -> None:
    frontend_env = ROOT / "app" / "frontend" / ".env"
    lines = [
        f"VITE_SUPABASE_URL={updates.get('SUPABASE_URL', 'http://127.0.0.1:54321')}",
        f"VITE_SUPABASE_ANON_KEY={updates.get('SUPABASE_ANON_KEY', '')}",
        "VITE_API_URL=http://127.0.0.1:8000",
    ]
    frontend_env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: updated {frontend_env}")


if __name__ == "__main__":
    raise SystemExit(main())
