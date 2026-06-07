"""Infile FEL adapter skeleton.

The adapter intentionally imports no Infile SDK/API client in this PR. FEL calls
must be made by asynchronous workers after the invoice Unit of Work commits; the
invoice posting service must enqueue outbox events instead of calling this
adapter synchronously.
"""

from __future__ import annotations

from shared.fel.ports import FelResult


class InfileFelProvider:
    """Import-safe skeleton for the future Infile adapter."""

    async def authorize(self, invoice_id: int) -> FelResult:
        raise NotImplementedError("Infile FEL authorization is not wired yet")

    async def cancel_or_credit(self, invoice_id: int, reason: str) -> FelResult:
        raise NotImplementedError("Infile FEL credit flow is not wired yet")
