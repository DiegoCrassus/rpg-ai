"""Load integration credentials from repo ``.env``, process env, and ``.sdlc/sdlc.yaml``."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

GITHUB_API = "https://api.github.com"
PLANE_API_DEFAULT = "https://api.plane.so"
_REPO_MARKER = ".sdlc/sdlc.yaml"


def discover_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / _REPO_MARKER).is_file():
            return candidate
    return current


def parse_env_file(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def load_dotenv(repo_root: Path) -> None:
    """Best-effort populate process env (does not override existing keys)."""
    for key, val in parse_env_file(repo_root).items():
        os.environ.setdefault(key, val)


@lru_cache(maxsize=8)
def _board_config(repo_root: str) -> dict[str, Any]:
    path = Path(repo_root) / ".sdlc" / "sdlc.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        vendors = (data.get("core") or {}).get("vendors") or {}
        return vendors.get("board") or vendors.get("workboard") or {}
    except (OSError, yaml.YAMLError):
        return {}


def _resolve(repo_root: Path, *keys: str, yaml_key: str | None = None, default: str = "") -> str:
    """Repo ``.env`` wins over stale shell exports, then ``os.environ``, then ``sdlc.yaml``."""
    file_env = parse_env_file(repo_root)
    for key in keys:
        val = file_env.get(key)
        if val and val.strip():
            return val.strip()
    for key in keys:
        val = os.environ.get(key)
        if val and val.strip():
            return val.strip()
    if yaml_key:
        cfg_val = _board_config(str(repo_root.resolve())).get(yaml_key)
        if cfg_val is not None and str(cfg_val).strip():
            return str(cfg_val).strip()
    return default


def card_prefix(repo_root: Path) -> str:
    return _resolve(repo_root, yaml_key="card_prefix", default="RPG")


def card_pattern(repo_root: Path) -> re.Pattern[str]:
    prefix = re.escape(card_prefix(repo_root))
    return re.compile(rf"^{prefix}-(\d+)$", re.IGNORECASE)


def parse_card(card: str, repo_root: Path) -> tuple[str, int]:
    match = card_pattern(repo_root).match(card.strip())
    if not match:
        prefix = card_prefix(repo_root)
        raise ValueError(f"invalid card {card!r} — expected {prefix}-N")
    seq = int(match.group(1))
    return f"{card_prefix(repo_root).upper()}-{seq}", seq


def format_card(sequence: int, repo_root: Path) -> str:
    return f"{card_prefix(repo_root).upper()}-{sequence}"


def plane_api_key(repo_root: Path) -> str | None:
    value = _resolve(repo_root, "PLANE_API_KEY", "BOARD_API_KEY")
    return value or None


def plane_workspace(repo_root: Path) -> str:
    return _resolve(
        repo_root,
        "PLANE_WORKSPACE_SLUG",
        "BOARD_WORKSPACE_SLUG",
        yaml_key="workspace",
        default="rpg",
    )


def plane_project_id(repo_root: Path) -> str:
    return _resolve(
        repo_root,
        "PLANE_PROJECT_ID",
        "BOARD_PROJECT_ID",
        yaml_key="project_id",
    )


def plane_base_url(repo_root: Path) -> str:
    return _resolve(repo_root, "PLANE_BASE_URL", default=PLANE_API_DEFAULT).rstrip("/")


def github_token(repo_root: Path) -> str | None:
    value = _resolve(
        repo_root,
        "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GH_TOKEN",
    )
    return value or None


def github_repository(repo_root: Path) -> str:
    slug = _resolve(repo_root, "REPOSITORY_SLUG", "GITHUB_REPOSITORY")
    if slug:
        return slug
    path = repo_root / ".sdlc" / "sdlc.yaml"
    if path.is_file():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            repository = (data.get("core") or {}).get("vendors", {}).get("repository") or {}
            owner = str(repository.get("owner") or "")
            name = str(repository.get("repository") or repository.get("name") or "")
            if owner and name:
                return f"{owner}/{name}"
        except (OSError, yaml.YAMLError):
            pass
    return "DiegoCrassus/sdlc-ai"
