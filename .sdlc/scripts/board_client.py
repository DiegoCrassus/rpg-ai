"""Vendor-neutral board + repository client helpers (Plane/GitHub implementations)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from re import Pattern

DSL = Path(__file__).resolve().parent.parent / "dsl"
if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

from core_config import (  # noqa: E402
    board,
    card_id,
    card_pattern,
    card_prefix,
    env_map,
    repository,
)

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _env(*keys: str, default: str = "") -> str:
    for key in keys:
        val = os.environ.get(key)
        if val:
            return val
    return default


def board_api() -> tuple[str, str, str]:
    """Return (api_key, workspace_slug, project_id) for the configured board provider."""
    _load_dotenv()
    logical = env_map(ROOT)
    cfg = board(ROOT)
    api_key = _env(
        logical.get("board_api_key", "BOARD_API_KEY"),
        "BOARD_API_KEY",
        logical.get("workboard_api_key", "PLANE_API_KEY"),
        "PLANE_API_KEY",
    )
    workspace = _env(
        "BOARD_WORKSPACE_SLUG",
        "PLANE_WORKSPACE_SLUG",
        str(cfg.get("workspace") or "RPG-AI"),
    )
    project_id = _env(
        "BOARD_PROJECT_ID",
        "PLANE_PROJECT_ID",
        str(cfg.get("project_id") or ""),
    )
    if not api_key:
        sys.exit("ERROR: board API key not set (BOARD_API_KEY or PLANE_API_KEY)")
    if not project_id:
        sys.exit("ERROR: board project id not set (BOARD_PROJECT_ID or PLANE_PROJECT_ID)")
    return api_key, workspace, project_id


def repository_api() -> tuple[str, str]:
    """Return (token, owner/repo) for the configured repository provider."""
    _load_dotenv()
    logical = env_map(ROOT)
    token = _env(
        logical.get("repository_token", "REPOSITORY_TOKEN"),
        "REPOSITORY_TOKEN",
        logical.get("vcs_token", "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC"),
        "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC",
        "GITHUB_TOKEN",
    )
    repo_cfg = repository(ROOT)
    owner = str(repo_cfg.get("owner") or "")
    name = str(repo_cfg.get("repository") or repo_cfg.get("name") or "")
    slug = _env("REPOSITORY_SLUG", "GITHUB_REPOSITORY", f"{owner}/{name}" if owner and name else "")
    if not token:
        sys.exit("ERROR: repository token not set (REPOSITORY_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC)")
    return token, slug


def repository_api_base() -> str:
    repo_cfg = repository(ROOT)
    host = str(repo_cfg.get("host") or "github.com")
    return f"https://api.{host}"


def repository_web_base() -> str:
    repo_cfg = repository(ROOT)
    host = str(repo_cfg.get("host") or "github.com")
    _, slug = repository_api()
    return f"https://{host}/{slug}"


def card_re() -> Pattern[str]:
    return card_pattern(ROOT)


def parse_card(card: str) -> int:
    m = card_re().match(card.strip())
    if not m:
        prefix = card_prefix(ROOT)
        sys.exit(f"ERROR: invalid card {card!r} — expected {prefix}-N")
    return int(m.group(1))


def format_card(sequence_id: int) -> str:
    return card_id(sequence_id, ROOT)
