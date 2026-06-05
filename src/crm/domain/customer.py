"""Customer domain primitives for the CRM bounded context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CustomerStatus(str, Enum):
    """Lifecycle states for customer master data."""

    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Contact:
    """Customer contact record."""

    id: int | None
    customer_id: int | None
    name: str
    email: str | None = None
    phone: str | None = None
    is_primary: bool = False


@dataclass(frozen=True)
class Customer:
    """Customer master record.

    `tax_id` is immutable after creation; update flows must not expose it as a
    mutable field.
    """

    id: int | None
    name: str
    tax_id: str
    email: str | None = None
    phone: str | None = None
    status: CustomerStatus = CustomerStatus.ACTIVE

    @property
    def is_active(self) -> bool:
        return self.status == CustomerStatus.ACTIVE
