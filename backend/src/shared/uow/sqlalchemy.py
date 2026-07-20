"""Async SQLAlchemy Unit of Work implementation."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SqlAlchemyUnitOfWork:
    """Transaction boundary backed by a single SQLAlchemy async session."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker
        self._session: AsyncSession | None = None
        self._committed = False

    @property
    def session(self) -> AsyncSession:
        """Return the active session for repository adapter construction."""
        if self._session is None:
            msg = "SqlAlchemyUnitOfWork session is only available inside a context"
            raise RuntimeError(msg)
        return self._session

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._sessionmaker()
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None and not self._committed:
                await self.rollback()
        finally:
            await self.session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit the active Unit of Work transaction once."""
        await self.session.commit()
        self._committed = True

    async def rollback(self) -> None:
        """Rollback the active Unit of Work transaction."""
        await self.session.rollback()
        self._committed = False
