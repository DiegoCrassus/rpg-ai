"""Studio Service settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_MARKER = ".sdlc/sdlc.yaml"


def discover_repo_root(start: Path | None = None) -> Path:
    """Walk parents from *start* until ``.sdlc/sdlc.yaml`` exists."""

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / _REPO_MARKER).is_file():
            return candidate
    return current


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STUDIO_", extra="ignore")

    app_name: str = "Studio Service API"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8100
    repo_root: Path | None = Field(default=None, description="SDLC repo root")
    obs_db_path: Path | None = Field(default=None, description="Override sdlc_obs SQLite path")
    cors_origins: str = "http://127.0.0.1:5174"
    auth_token: str | None = Field(
        default=None,
        description="When set, /studio/* requires Authorization: Bearer <token>",
    )

    @property
    def resolved_repo_root(self) -> Path:
        return (self.repo_root or discover_repo_root()).resolve()

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_obs_db_path(self) -> Path:
        if self.obs_db_path:
            return self.obs_db_path.resolve()
        return self.resolved_repo_root / "app/infra/sdlc_obs/data/sdlc_obs.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
