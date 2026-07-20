from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.uow.sqlalchemy import SqlAlchemyUnitOfWork


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


def make_uow(
    sessionmaker: Callable[[], FakeAsyncSession],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(
        cast(async_sessionmaker[AsyncSession], sessionmaker)
    )


@pytest.mark.asyncio
async def test_sqlalchemy_unit_of_work_commits_session_once_on_commit() -> None:
    session = FakeAsyncSession()
    sessionmaker = FakeAsyncSessionMaker(session)
    uow = make_uow(sessionmaker)

    async with uow as opened_uow:
        assert opened_uow is uow
        await opened_uow.commit()

    assert sessionmaker.calls == 1
    assert session.commits == 1
    assert session.rollbacks == 0
    assert session.closes == 1


@pytest.mark.asyncio
async def test_sqlalchemy_unit_of_work_rolls_back_on_exception() -> None:
    session = FakeAsyncSession()
    sessionmaker = FakeAsyncSessionMaker(session)
    uow = make_uow(sessionmaker)

    with pytest.raises(RuntimeError, match="application failure"):
        async with uow:
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
