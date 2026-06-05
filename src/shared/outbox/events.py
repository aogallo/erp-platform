"""Provider-neutral event contracts for asynchronous FEL workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class FelEventType(str, Enum):
    """Outbox event names aligned to invoice/FEL lifecycle transitions."""

    POSTED_PENDING_FEL = "posted_pending_fel"
    FEL_AUTHORIZED = "fel_authorized"
    FEL_FAILED = "fel_failed"
    CREDITED = "credited"


@dataclass(frozen=True)
class OutboxEvent:
    """Event persisted inside the same transaction as local state changes."""

    event_type: FelEventType
    aggregate_type: str
    aggregate_id: int
    payload: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None


@dataclass(frozen=True)
class FelAuthorizationRequested:
    """Payload for `posted_pending_fel` events."""

    invoice_id: int


@dataclass(frozen=True)
class FelAuthorized:
    """Payload for `fel_authorized` events."""

    invoice_id: int
    fel_uuid: str
    document_number: str


@dataclass(frozen=True)
class FelFailed:
    """Payload for `fel_failed` events."""

    invoice_id: int
    reason: str
    retryable: bool


@dataclass(frozen=True)
class InvoiceCredited:
    """Payload for `credited` events."""

    invoice_id: int
    credit_note_id: int | None
    reason: str
