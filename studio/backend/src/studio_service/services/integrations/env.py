"""Load integration credentials from process env and repo ``.env``."""

from __future__ import annotations

import os
import re
from pathlib import Path

CARD_RE = re.compile(r"^INVES-(\d+)$", re.IGNORECASE)
DEFAULT_PLANE_PROJECT_ID = "04ac3a5d-7457-40f3-b94f-fccd4c29a589"
GITHUB_API = "https://api.github.com"
PLANE_API_DEFAULT = "https://api.plane.so"


def load_dotenv(repo_root: Path) -> None:
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def parse_card(card: str) -> tuple[str, int]:
    m = CARD_RE.match(card.strip())
    if not m:
        raise ValueError(f"invalid card {card!r} — expected INVES-N")
    seq = int(m.group(1))
    return f"INVES-{seq}", seq


def _non_empty(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def plane_api_key() -> str | None:
    return _non_empty("PLANE_API_KEY")


def plane_workspace() -> str:
    return os.environ.get("PLANE_WORKSPACE_SLUG", "investments-sdlc")


def plane_project_id() -> str:
    return os.environ.get("PLANE_PROJECT_ID", DEFAULT_PLANE_PROJECT_ID)


def plane_base_url() -> str:
    return (os.environ.get("PLANE_BASE_URL") or PLANE_API_DEFAULT).rstrip("/")


def github_token() -> str | None:
    for name in (
        "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GH_TOKEN",
    ):
        value = _non_empty(name)
        if value:
            return value
    return None


def github_repository() -> str:
    return os.environ.get("GITHUB_REPOSITORY", "DiegoCrassus/sdlc-ai")
