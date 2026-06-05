"""Provider-neutral Guatemala FEL contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class FelStatus(str, Enum):
    """Provider-neutral FEL result status."""

    AUTHORIZED = "authorized"
    FAILED = "failed"
    RETRYABLE_FAILURE = "retryable_failure"


@dataclass(frozen=True)
class FelResult:
    """Result returned by a FEL provider adapter."""

    status: FelStatus
    fel_uuid: str | None = None
    document_number: str | None = None
    message: str | None = None


class FelProvider(Protocol):
    """Outbound FEL port used by asynchronous workers only."""

    async def authorize(self, invoice_id: int) -> FelResult:
        """Authorize a locally posted invoice asynchronously after commit."""

    async def cancel_or_credit(self, invoice_id: int, reason: str) -> FelResult:
        """Request the provider-side credit/cancellation flow."""
