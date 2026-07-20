from __future__ import annotations

from typing import Optional, cast

import pytest
from sqlalchemy import ForeignKey, Integer, MetaData, String, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.sqlalchemy import Base, create_async_sessionmaker, create_engine


def test_declarative_base_uses_shared_metadata_naming_conventions() -> None:
    class SqlAlchemyFoundationTenant(Base):
        __tablename__ = "sqlalchemy_foundation_tenants"
        __table_args__ = (UniqueConstraint("code"), {"schema": "iam"})

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        code: Mapped[str] = mapped_column(String(32), nullable=False)

    class SqlAlchemyFoundationUser(Base):
        __tablename__ = "sqlalchemy_foundation_users"
        __table_args__ = {"schema": "iam"}

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        tenant_id: Mapped[int] = mapped_column(
            ForeignKey("iam.sqlalchemy_foundation_tenants.id"), nullable=False
        )
        email: Mapped[str] = mapped_column(String(255), nullable=False)

    assert isinstance(Base.metadata, MetaData)
    assert Base.metadata.naming_convention == {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    assert SqlAlchemyFoundationTenant.metadata is Base.metadata
    tenant_table = cast(Table, SqlAlchemyFoundationTenant.__table__)
    user_table = cast(Table, SqlAlchemyFoundationUser.__table__)
    tenant_constraint_names = {
        str(constraint.name) for constraint in tenant_table.constraints
    }
    user_constraint_names = {
        str(constraint.name) for constraint in user_table.constraints
    }

    assert tenant_table.primary_key.name == (
        "pk_sqlalchemy_foundation_tenants"
    )
    assert user_table.primary_key.name == (
        "pk_sqlalchemy_foundation_users"
    )
    assert tenant_constraint_names >= {
        "pk_sqlalchemy_foundation_tenants",
        "uq_sqlalchemy_foundation_tenants_code",
    }
    assert user_constraint_names >= {
        "pk_sqlalchemy_foundation_users",
        "fk_sqlalchemy_foundation_users_tenant_id_sqlalchemy_foundation_tenants",
    }


def test_create_engine_builds_async_engine_without_connecting() -> None:
    engine = create_engine(
        "postgresql+psycopg://erp_user:secret@database.local:6543/erp_platform_test",
        echo=True,
    )

    try:
        assert isinstance(engine, AsyncEngine)
        assert engine.echo is True
        assert engine.url.render_as_string(hide_password=False) == (
            "postgresql+psycopg://erp_user:secret@database.local:6543/erp_platform_test"
        )
    finally:
        engine.sync_engine.dispose()


@pytest.mark.asyncio
async def test_create_async_sessionmaker_wires_async_sessions_to_engine() -> None:
    engine = create_engine(
        "postgresql+psycopg://erp_user:secret@database.local:6543/erp_platform_test"
    )
    sessionmaker = create_async_sessionmaker(engine)

    session: Optional[AsyncSession] = None
    try:
        session = sessionmaker()

        assert isinstance(session, AsyncSession)
        assert session.bind is engine
        assert session.sync_session.expire_on_commit is False
        assert session.sync_session.autoflush is False
    finally:
        if session is not None:
            await session.close()
        engine.sync_engine.dispose()
