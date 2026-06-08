"""Typed environment-backed settings for the backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


DEFAULT_APP_NAME = "ERP Platform API"
DEFAULT_APP_VERSION = "0.1.0"
DEFAULT_DATABASE_HOST = "localhost"
DEFAULT_DATABASE_PORT = 5432
DEFAULT_DATABASE_NAME = "erp"
DEFAULT_DATABASE_USER = "erp"
DEFAULT_DATABASE_PASSWORD = "erp_dev_password"


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime configuration consumed by backend wiring."""

    app_name: str = DEFAULT_APP_NAME
    app_version: str = DEFAULT_APP_VERSION
    database_host: str = DEFAULT_DATABASE_HOST
    database_port: int = DEFAULT_DATABASE_PORT
    database_name: str = DEFAULT_DATABASE_NAME
    database_user: str = DEFAULT_DATABASE_USER
    database_password: str = DEFAULT_DATABASE_PASSWORD

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from the process environment."""
        return cls(
            app_name=os.environ.get("ERP_APP_NAME", DEFAULT_APP_NAME),
            app_version=os.environ.get("ERP_APP_VERSION", DEFAULT_APP_VERSION),
            database_host=os.environ.get("ERP_DATABASE_HOST", DEFAULT_DATABASE_HOST),
            database_port=int(
                os.environ.get("ERP_DATABASE_PORT", DEFAULT_DATABASE_PORT)
            ),
            database_name=os.environ.get("ERP_DATABASE_NAME", DEFAULT_DATABASE_NAME),
            database_user=os.environ.get("ERP_DATABASE_USER", DEFAULT_DATABASE_USER),
            database_password=os.environ.get(
                "ERP_DATABASE_PASSWORD", DEFAULT_DATABASE_PASSWORD
            ),
        )

    @property
    def database_url(self) -> str:
        """Return the SQLAlchemy-compatible PostgreSQL connection URL."""
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings for dependency wiring."""
    return Settings.from_env()
