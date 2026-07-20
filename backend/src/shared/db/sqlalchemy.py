"""SQLAlchemy async infrastructure shared by persistence adapters.

Flyway SQL migrations remain the database source of truth. Future bounded-context
ORM models should live in `backend/src/{context}/repositories/models.py` and map
the committed SQL shape instead of generating independent schema changes.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for future bounded-context repository models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def create_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Create the application async SQLAlchemy engine without opening a connection."""
    return create_async_engine(database_url, echo=echo)


def create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create the async session factory used by Unit of Work implementations."""
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
