"""Repository contracts for Sales invoice persistence adapters."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from src.sales.domain.invoice import Invoice, InvoiceStatus


class InvoiceRepository(Protocol):
    """Persistence port for invoice records."""

    async def add(self, invoice: Invoice) -> Invoice:
        """Persist a new draft invoice."""

    async def get(self, invoice_id: int) -> Invoice | None:
        """Return an invoice by ID."""

    async def save(self, invoice: Invoice) -> Invoice:
        """Persist invoice changes."""

    async def query(
        self,
        *,
        invoice_number: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        customer_id: int | None = None,
        status: InvoiceStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Invoice], int]:
        """Return paginated invoices and total count."""

    async def mark_posted_pending_fel(self, invoice_id: int) -> None:
        """Mark a draft invoice as locally posted and pending FEL."""

    async def mark_fel_authorized(
        self, invoice_id: int, *, fel_uuid: str, document_number: str
    ) -> None:
        """Store FEL authorization metadata."""

    async def mark_fel_failed(self, invoice_id: int, *, reason: str) -> None:
        """Mark FEL authorization as failed without reversing local posting."""

    async def mark_credited(self, invoice_id: int) -> None:
        """Mark an invoice as credited after credit note workflow completes."""
