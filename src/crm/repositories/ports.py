"""Repository contracts for CRM customer persistence adapters."""

from __future__ import annotations

from typing import Protocol

from src.crm.domain.customer import Contact, Customer
from src.shared.pagination import Page


class CustomerRepository(Protocol):
    """Persistence port for customer master data."""

    async def tax_id_exists(self, tax_id: str) -> bool:
        """Return whether a customer already exists with the given tax ID."""

    async def add(self, customer: Customer) -> Customer:
        """Persist a new customer and return it with a generated ID."""

    async def get(self, customer_id: int) -> Customer | None:
        """Return a customer by ID, including disabled customers."""

    async def save(self, customer: Customer) -> Customer:
        """Persist customer changes."""

    async def search(
        self,
        *,
        name: str | None = None,
        tax_id: str | None = None,
        email: str | None = None,
        include_disabled: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Page[Customer]:
        """Return a named paginated customer result."""

    async def add_contact(self, contact: Contact) -> Contact:
        """Attach a contact to a customer."""

    async def remove_contact(self, customer_id: int, contact_id: int) -> None:
        """Remove a contact from a customer."""
