"""IAM local policy contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from shared.auth.contracts import SessionStatus, ensure_utc


class UserStatus(StrEnum):
    """Local IAM user lifecycle status."""

    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    active: bool


@dataclass(frozen=True)
class LocalUser:
    user_id: str
    provider_subject: str
    email: str | None
    status: UserStatus


@dataclass(frozen=True)
class TenantMembership:
    user_id: str
    tenant_id: str
    active: bool


@dataclass(frozen=True)
class Role:
    role_id: str
    tenant_id: str
    name: str


@dataclass(frozen=True)
class Permission:
    permission_id: str
    name: str


@dataclass(frozen=True)
class LocalSession:
    session_id: str
    user_id: str
    status: SessionStatus
    expires_at: datetime

    def __post_init__(self) -> None:
        ensure_utc(self.expires_at, "expires_at")


@dataclass(frozen=True)
class Invitation:
    invitation_id: str
    tenant_id: str
    email: str
    accepted: bool
