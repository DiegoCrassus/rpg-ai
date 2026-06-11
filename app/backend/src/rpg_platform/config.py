"""Application settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///:memory:"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_database_url(value)
        return value
    supabase_url: str = "http://127.0.0.1:54321"
    supabase_service_role_key: str = "test-service-role-key"
    supabase_jwt_secret: str = "test-jwt-secret-for-local-dev-only"
    cors_origins: str = "http://localhost:5173"
    agent_model: str = "openai:gpt-4.1-mini"
    openai_api_key: str = ""
    import_job_timeout_seconds: int = 120
    import_rate_limit_per_hour: int = 5
    signed_url_ttl_seconds: int = 3600
    app_env: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
