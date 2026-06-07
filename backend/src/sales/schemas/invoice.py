"""Import-safe invoice request/response shape placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from sales.domain.invoice import InvoiceStatus


@dataclass(frozen=True)
class InvoiceLineCreate:
    product_id: int
    quantity: Decimal
    unit_price: Decimal


@dataclass(frozen=True)
class InvoiceCreate:
    customer_id: int
    line_items: tuple[InvoiceLineCreate, ...]


@dataclass(frozen=True)
class InvoiceUpdate:
    line_items: tuple[InvoiceLineCreate, ...] | None = None


@dataclass(frozen=True)
class CreditNoteCreate:
    reason: str


@dataclass(frozen=True)
class InvoiceQuery:
    invoice_number: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    customer_id: int | None = None
    status: InvoiceStatus | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class InvoiceRead:
    id: int
    customer_id: int
    status: InvoiceStatus
    total: Decimal
    fel_uuid: str | None = None
    fel_document_number: str | None = None


@dataclass(frozen=True)
class Page:
    items: tuple[InvoiceRead, ...]
    total: int
    page: int
    page_size: int
