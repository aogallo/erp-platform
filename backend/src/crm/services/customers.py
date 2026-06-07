"""Application service contract for customer workflows."""

from __future__ import annotations

from typing import Protocol

from crm.schemas.customer import (
    ContactCreate,
    CustomerCreate,
    CustomerRead,
    CustomerSearch,
    CustomerUpdate,
)
from shared.pagination import Page


class CustomerService(Protocol):
    """Application boundary for CRM customer use cases."""

    async def create_customer(self, command: CustomerCreate) -> CustomerRead:
        """Create a customer, enforcing unique tax IDs."""

    async def update_customer(
        self, customer_id: int, command: CustomerUpdate
    ) -> CustomerRead:
        """Update mutable customer fields; tax IDs remain immutable."""

    async def search_customers(self, query: CustomerSearch) -> Page[CustomerRead]:
        """Search active customers by name, tax ID, or email."""

    async def disable_customer(self, customer_id: int) -> None:
        """Soft-disable a customer."""

    async def add_contact(
        self, customer_id: int, command: ContactCreate
    ) -> None:
        """Add a contact to a customer."""

    async def remove_contact(self, customer_id: int, contact_id: int) -> None:
        """Remove a contact from a customer."""
