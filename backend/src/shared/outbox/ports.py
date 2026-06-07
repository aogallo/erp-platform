"""Ports for transactional outbox persistence and dispatch."""

from __future__ import annotations

from typing import Protocol
from shared.outbox.events import OutboxEvent


class OutboxRepository(Protocol):
    """Persistence port for outbox events."""

    async def add(self, event: OutboxEvent) -> OutboxEvent:
        """Persist an event in the current Unit of Work transaction."""

    async def get_pending(self, *, limit: int = 100) -> list[OutboxEvent]:
        """Return pending events for an asynchronous worker."""

    async def mark_dispatched(self, event_id: int) -> None:
        """Mark an event as successfully dispatched."""

    async def mark_failed(self, event_id: int, *, reason: str) -> None:
        """Record a dispatch failure without changing local business commits."""
