"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///:memory:"
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
