"""Invoice domain primitives for the Sales bounded context."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice lifecycle states from the canonical invoice specification."""

    DRAFT = "draft"
    POSTED_PENDING_FEL = "posted_pending_fel"
    FEL_AUTHORIZED = "fel_authorized"
    FEL_FAILED = "fel_failed"
    CREDITED = "credited"


@dataclass(frozen=True)
class InvoiceLine:
    id: int | None
    product_id: int
    quantity: Decimal
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class Invoice:
    id: int | None
    customer_id: int
    lines: tuple[InvoiceLine, ...]
    status: InvoiceStatus = InvoiceStatus.DRAFT
    fel_uuid: str | None = None
    fel_document_number: str | None = None

    @property
    def is_mutable(self) -> bool:
        return self.status == InvoiceStatus.DRAFT

    @property
    def can_request_fel_authorization(self) -> bool:
        return self.status in {
            InvoiceStatus.POSTED_PENDING_FEL,
            InvoiceStatus.FEL_FAILED,
        }
