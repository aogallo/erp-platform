"""Application service contract for invoice workflows."""

from __future__ import annotations

from typing import Protocol

from sales.schemas.invoice import (
    CreditNoteCreate,
    InvoiceCreate,
    InvoiceQuery,
    InvoiceRead,
    InvoiceUpdate,
)
from shared.pagination import Page


class InvoiceService(Protocol):
    """Application boundary for Sales invoice use cases."""

    async def create_invoice(self, command: InvoiceCreate) -> InvoiceRead:
        """Create a draft invoice for an active customer."""

    async def update_invoice(
        self, invoice_id: int, command: InvoiceUpdate
    ) -> InvoiceRead:
        """Update a mutable draft invoice."""

    async def delete_invoice(self, invoice_id: int) -> None:
        """Delete a mutable draft invoice."""

    async def post_invoice(self, invoice_id: int) -> InvoiceRead:
        """Post a draft invoice locally and enqueue asynchronous FEL."""

    async def create_credit_note(
        self, invoice_id: int, command: CreditNoteCreate
    ) -> InvoiceRead:
        """Credit a FEL-authorized invoice through the reversal workflow."""

    async def retry_fel_authorization(self, invoice_id: int) -> None:
        """Queue a new FEL authorization attempt without duplicating posting."""

    async def query_invoices(self, query: InvoiceQuery) -> Page[InvoiceRead]:
        """Search invoices by number, date range, customer, or status."""
