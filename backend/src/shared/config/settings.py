"""Typed environment-backed settings for the backend."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_APP_NAME = "ERP Platform API"
DEFAULT_APP_VERSION = "0.1.0"
DEFAULT_DATABASE_HOST = "localhost"
DEFAULT_DATABASE_PORT = 5432
DEFAULT_DATABASE_NAME = "erp_platform_dev"
DEFAULT_DATABASE_USER = "erp"
DEFAULT_DATABASE_PASSWORD = "erp_dev_password"
DEFAULT_AUTH_SESSION_MAX_AGE_MINUTES = 480
DEFAULT_AUTH_SESSION_IDLE_TIMEOUT_MINUTES = 60


class Settings(BaseSettings):
    """Runtime configuration consumed by backend wiring."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ERP_",
        extra="ignore",
        frozen=True,
    )

    app_name: str = DEFAULT_APP_NAME
    app_version: str = DEFAULT_APP_VERSION
    database_host: str = DEFAULT_DATABASE_HOST
    database_port: int = DEFAULT_DATABASE_PORT
    database_name: str = DEFAULT_DATABASE_NAME
    database_user: str = DEFAULT_DATABASE_USER
    database_password: str = DEFAULT_DATABASE_PASSWORD
    auth_issuer: str = ""
    auth_audience: str = ""
    auth_jwks_url: str = ""
    auth_session_max_age_minutes: int = DEFAULT_AUTH_SESSION_MAX_AGE_MINUTES
    auth_session_idle_timeout_minutes: int = DEFAULT_AUTH_SESSION_IDLE_TIMEOUT_MINUTES
    auth_session_revocation_required: bool = True

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from process environment and local `.env` fallback."""
        return cls()

    @property
    def database_url(self) -> str:
        """Return the SQLAlchemy-compatible PostgreSQL connection URL."""
        return self.sqlalchemy_async_database_url

    @property
    def sqlalchemy_async_database_url(self) -> str:
        """Return the async SQLAlchemy PostgreSQL connection URL."""
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings for dependency wiring."""
    return Settings.from_env()
