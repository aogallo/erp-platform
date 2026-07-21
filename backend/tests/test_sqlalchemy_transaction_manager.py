from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.transactions.sqlalchemy import SqlAlchemyTransactionManager


class FakeAsyncSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1

    async def close(self) -> None:
        self.closes += 1


class FakeAsyncSessionMaker:
    def __init__(self, session: FakeAsyncSession) -> None:
        self.session = session
        self.calls = 0

    def __call__(self) -> FakeAsyncSession:
        self.calls += 1
        return self.session


def make_transaction_manager(
    sessionmaker: Callable[[], FakeAsyncSession],
) -> SqlAlchemyTransactionManager:
    return SqlAlchemyTransactionManager(
        cast(async_sessionmaker[AsyncSession], sessionmaker)
    )


@pytest.mark.asyncio
async def test_sqlalchemy_transaction_manager_commits_session_once_on_commit() -> None:
    session = FakeAsyncSession()
    sessionmaker = FakeAsyncSessionMaker(session)
    transaction_manager = make_transaction_manager(sessionmaker)

    async with transaction_manager as opened_transaction_manager:
        assert opened_transaction_manager is transaction_manager
        await opened_transaction_manager.commit()

    assert sessionmaker.calls == 1
    assert session.commits == 1
    assert session.rollbacks == 0
    assert session.closes == 1


@pytest.mark.asyncio
async def test_sqlalchemy_transaction_manager_rolls_back_on_exception() -> None:
    session = FakeAsyncSession()
    sessionmaker = FakeAsyncSessionMaker(session)
    transaction_manager = make_transaction_manager(sessionmaker)

    with pytest.raises(RuntimeError, match="application failure"):
        async with transaction_manager:
            raise RuntimeError("application failure")

    assert sessionmaker.calls == 1
    assert session.commits == 0
    assert session.rollbacks == 1
    assert session.closes == 1


def test_repository_files_do_not_call_raw_session_commit() -> None:
    repository_files = sorted(Path("backend/src").glob("**/repositories/*.py"))

    assert repository_files
    assert [
        repository_file
        for repository_file in repository_files
        if "session.commit(" in repository_file.read_text(encoding="utf-8")
    ] == []
