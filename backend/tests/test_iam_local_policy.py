from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from iam.contracts import LocalSession, LocalUser, TenantMembership, UserStatus
from iam.services.local_policy import LocalIamPolicyService
from shared.auth.contracts import SessionStatus, TokenValidationResult


class InMemoryIamRepository:
    def __init__(
        self,
        *,
        user: LocalUser,
        membership: TenantMembership | None,
        session: LocalSession,
        permissions: frozenset[str],
    ) -> None:
        self.user = user
        self.membership = membership
        self.session = session
        self.permissions = permissions

    async def get_user_by_provider_subject(
        self, provider_subject: str
    ) -> LocalUser | None:
        if provider_subject == self.user.provider_subject:
            return self.user
        return None

    async def get_tenant_membership(
        self, *, user_id: str, tenant_id: str
    ) -> TenantMembership | None:
        if (
            self.membership is not None
            and self.membership.user_id == user_id
            and self.membership.tenant_id == tenant_id
        ):
            return self.membership
        return None

    async def get_session(self, session_id: str) -> LocalSession | None:
        if session_id == self.session.session_id:
            return self.session
        return None

    async def list_permissions(
        self, *, user_id: str, tenant_id: str
    ) -> frozenset[str]:
        if user_id == self.user.user_id and tenant_id == "tenant-a":
            return self.permissions
        return frozenset()


def make_token(
    *,
    provider_subject: str = "auth0|subject-10",
    issuer: str = "https://tenant.auth0.com/",
    audience: str = "https://api.erp.test",
    email: str | None = "admin@acme.test",
    claims: dict[str, Any] | None = None,
) -> TokenValidationResult:
    issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    return TokenValidationResult(
        provider_subject=provider_subject,
        issuer=issuer,
        audience=audience,
        issued_at=issued_at,
        expires_at=issued_at + timedelta(minutes=15),
        email=email,
        claims=claims or {"roles": ["admin"]},
    )


def make_repository(
    *,
    user_status: UserStatus = UserStatus.ACTIVE,
    membership_active: bool = True,
    session_status: SessionStatus = SessionStatus.ACTIVE,
    permissions: frozenset[str] = frozenset({"sales.invoice.post"}),
) -> InMemoryIamRepository:
    issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    return InMemoryIamRepository(
        user=LocalUser(
            user_id="user-10",
            provider_subject="auth0|subject-10",
            email="admin@acme.test",
            status=user_status,
        ),
        membership=TenantMembership(
            user_id="user-10",
            tenant_id="tenant-a",
            active=membership_active,
        ),
        session=LocalSession(
            session_id="session-10",
            user_id="user-10",
            status=session_status,
            expires_at=issued_at + timedelta(minutes=15),
        ),
        permissions=permissions,
    )


def test_local_session_requires_utc_expiry() -> None:
    with pytest.raises(ValueError, match="expires_at must be timezone-aware UTC"):
        LocalSession(
            session_id="session-10",
            user_id="user-10",
            status=SessionStatus.ACTIVE,
            expires_at=datetime(2026, 7, 1, 12, 0),
        )


@pytest.mark.asyncio
async def test_local_policy_requires_explicit_tenant_membership() -> None:
    repository = make_repository(membership_active=False)
    service = LocalIamPolicyService(repository=repository)

    with pytest.raises(PermissionError, match="Tenant membership is not active"):
        await service.build_principal(
            token=make_token(), tenant_id="tenant-a", session_id="session-10"
        )


@pytest.mark.asyncio
async def test_local_policy_rejects_disabled_users_with_valid_provider_token() -> None:
    repository = make_repository(user_status=UserStatus.DISABLED)
    service = LocalIamPolicyService(repository=repository)

    with pytest.raises(PermissionError, match="Local user is disabled"):
        await service.build_principal(
            token=make_token(), tenant_id="tenant-a", session_id="session-10"
        )


@pytest.mark.asyncio
async def test_local_policy_rejects_revoked_sessions() -> None:
    repository = make_repository(session_status=SessionStatus.REVOKED)
    service = LocalIamPolicyService(repository=repository)

    with pytest.raises(PermissionError, match="Local session is not active"):
        await service.build_principal(
            token=make_token(), tenant_id="tenant-a", session_id="session-10"
        )


@pytest.mark.asyncio
async def test_local_policy_uses_removed_local_permissions() -> None:
    repository = make_repository(permissions=frozenset({"crm.customer.read"}))
    service = LocalIamPolicyService(repository=repository)

    principal = await service.build_principal(
        token=make_token(),
        tenant_id="tenant-a",
        session_id="session-10",
        now=datetime(2026, 7, 1, 12, 1, tzinfo=UTC),
    )

    assert principal.permissions == frozenset({"crm.customer.read"})
    assert "sales.invoice.post" not in principal.permissions


@pytest.mark.asyncio
async def test_local_policy_ignores_provider_role_claims_for_permissions() -> None:
    repository = make_repository(permissions=frozenset({"sales.invoice.read"}))
    service = LocalIamPolicyService(repository=repository)

    principal = await service.build_principal(
        token=make_token(claims={"roles": ["admin", "superuser"]}),
        tenant_id="tenant-a",
        session_id="session-10",
        now=datetime(2026, 7, 1, 12, 1, tzinfo=UTC),
    )

    assert principal.permissions == frozenset({"sales.invoice.read"})
