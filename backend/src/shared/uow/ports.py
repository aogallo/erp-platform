"""Shared Unit of Work and cross-context coordination ports."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from accounting.repositories.contracts import AccountingCostCenterLookupPort
from crm.repositories.ports import CustomerRepository
from hr.repositories.contracts import HROrganizationRepository
from sales.repositories.ports import InvoiceRepository
from shared.outbox.ports import OutboxRepository


class CustomerLookupPort(Protocol):
    """Read port used by Sales to validate customer usability."""

    async def is_active_customer(self, customer_id: int) -> bool:
        """Return whether a customer exists and is active."""

    async def tax_id_exists(self, tax_id: str) -> bool:
        """Return whether a customer tax ID is already registered."""


class InventoryCoordinationPort(Protocol):
    """Port for inventory effects coordinated during invoice posting."""

    async def deduct_for_invoice(self, invoice_id: int) -> None:
        """Deduct stock for all invoice lines inside the local transaction."""

    async def restore_for_credit_note(self, invoice_id: int) -> None:
        """Restore stock when a credit note reverses an invoice."""


class AccountingCoordinationPort(Protocol):
    """Port for accounting effects coordinated during invoice workflows."""

    async def create_invoice_entry(self, invoice_id: int, amount: Decimal) -> None:
        """Create the journal entry for a posted invoice."""

    async def create_credit_note_reversal(
        self, invoice_id: int, amount: Decimal
    ) -> None:
        """Create reversing entries for a credit note."""


class UnitOfWork(Protocol):
    """Transaction boundary for application use cases.

    Implementations own rollback on failure. Services prepare all local changes
    and outbox records before calling `commit()` exactly once.
    """

    customers: CustomerRepository
    customer_lookup: CustomerLookupPort
    invoices: InvoiceRepository
    inventory: InventoryCoordinationPort
    accounting: AccountingCoordinationPort
    accounting_cost_centers: AccountingCostCenterLookupPort
    hr_organization: HROrganizationRepository
    outbox: OutboxRepository

    async def __aenter__(self) -> UnitOfWork:
        """Open the Unit of Work transaction scope."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Rollback uncommitted work when the scope exits with an error."""

    async def commit(self) -> None:
        """Commit the local transaction."""

    async def rollback(self) -> None:
        """Rollback the local transaction."""
