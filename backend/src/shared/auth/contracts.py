"""Provider-neutral authentication and authorization contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol


class SessionStatus(StrEnum):
    """Local ERP session status values checked on every request."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISABLED = "disabled"


def ensure_utc(value: datetime, field_name: str) -> None:
    """Raise ValueError when a datetime is not timezone-aware UTC."""

    if value.tzinfo is not UTC:
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def _empty_claims() -> dict[str, Any]:
    return {}


@dataclass(frozen=True)
class TokenValidationResult:
    """Cryptographically validated provider token claims."""

    provider_subject: str
    issuer: str
    audience: str
    issued_at: datetime
    expires_at: datetime
    email: str | None = None
    claims: dict[str, Any] = field(default_factory=_empty_claims)

    def __post_init__(self) -> None:
        ensure_utc(self.issued_at, "issued_at")
        ensure_utc(self.expires_at, "expires_at")


@dataclass(frozen=True)
class Principal:
    """Local ERP actor resolved from provider identity and IAM policy."""

    user_id: str
    tenant_id: str
    provider_subject: str
    email: str | None
    permissions: frozenset[str]
    issued_at: datetime
    expires_at: datetime
    session_status: SessionStatus
    session_id: str | None = None

    def __post_init__(self) -> None:
        ensure_utc(self.issued_at, "issued_at")
        ensure_utc(self.expires_at, "expires_at")


class AuthProvider(Protocol):
    """Swappable auth contract consumed by controllers and services."""

    async def principal_from_bearer(
        self, token: str, tenant_id: str | None = None
    ) -> Principal:
        """Validate a bearer token and resolve the local ERP principal."""

    def require_permission(self, principal: Principal, permission: str) -> None:
        """Raise when the principal lacks a local ERP permission."""


def require_permission(principal: Principal, permission: str) -> None:
    """Raise PermissionError when the local principal lacks a permission."""

    if permission not in principal.permissions:
        raise PermissionError(f"Missing required permission: {permission}")
