"""Authentication and authorization provider contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Principal:
    """Authenticated actor plus tenant and RBAC claims."""

    subject: str
    tenant_id: str
    roles: frozenset[str]
    permissions: frozenset[str]


class AuthProvider(Protocol):
    """Swappable auth port consumed by controllers and services."""

    async def authenticate(self, username: str, password: str) -> Principal:
        """Authenticate credentials and return a principal."""

    def require_permission(self, principal: Principal, permission: str) -> None:
        """Raise when the principal lacks a required permission."""
