"""Import-safe customer request/response shape placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from crm.domain.customer import CustomerStatus


@dataclass(frozen=True)
class CustomerCreate:
    name: str
    tax_id: str
    email: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class CustomerUpdate:
    name: str | None = None
    email: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class ContactCreate:
    name: str
    email: str | None = None
    phone: str | None = None
    is_primary: bool = False


@dataclass(frozen=True)
class CustomerSearch:
    name: str | None = None
    tax_id: str | None = None
    email: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class CustomerRead:
    id: int
    name: str
    tax_id: str
    email: str | None
    phone: str | None
    status: CustomerStatus
