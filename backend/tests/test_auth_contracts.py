from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.auth.contracts import (
    AuthProvider,
    Principal,
    SessionStatus,
    TokenValidationResult,
    require_permission,
)


class FakeAuthProvider:
    def __init__(self, principal: Principal) -> None:
        self._principal = principal

    async def principal_from_bearer(
        self, token: str, tenant_id: str | None = None
    ) -> Principal:
        if token != "valid-access-token":
            raise PermissionError("Invalid bearer token")
        if tenant_id is not None and tenant_id != self._principal.tenant_id:
            raise PermissionError("Tenant scope is not allowed")
        return self._principal

    def require_permission(self, principal: Principal, permission: str) -> None:
        require_permission(principal, permission)


def make_principal(
    *, permissions: frozenset[str] = frozenset({"sales.invoice.post"})
) -> Principal:
    issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    return Principal(
        user_id="user-10",
        tenant_id="tenant-a",
        provider_subject="auth0|subject-10",
        email="admin@acme.test",
        permissions=permissions,
        issued_at=issued_at,
        expires_at=issued_at + timedelta(minutes=15),
        session_status=SessionStatus.ACTIVE,
        session_id="session-10",
    )


@pytest.mark.asyncio
async def test_auth_provider_returns_local_principal_from_bearer_token() -> None:
    principal = make_principal()
    provider: AuthProvider = FakeAuthProvider(principal)

    result = await provider.principal_from_bearer(
        "valid-access-token", tenant_id="tenant-a"
    )

    assert result == principal
    assert result.user_id == "user-10"
    assert result.tenant_id == "tenant-a"
    assert result.provider_subject == "auth0|subject-10"
    assert result.permissions == frozenset({"sales.invoice.post"})
    assert result.issued_at.tzinfo is UTC
    assert result.expires_at.tzinfo is UTC
    assert result.session_status is SessionStatus.ACTIVE


def test_require_permission_uses_local_permissions_only() -> None:
    principal = make_principal(permissions=frozenset({"crm.customer.read"}))

    require_permission(principal, "crm.customer.read")

    with pytest.raises(PermissionError, match="sales.invoice.post"):
        require_permission(principal, "sales.invoice.post")


def test_principal_requires_utc_issue_and_expiry_timestamps() -> None:
    issued_at = datetime(2026, 7, 1, 12, 0)

    with pytest.raises(ValueError, match="issued_at must be timezone-aware UTC"):
        Principal(
            user_id="user-10",
            tenant_id="tenant-a",
            provider_subject="auth0|subject-10",
            email=None,
            permissions=frozenset(),
            issued_at=issued_at,
            expires_at=datetime(2026, 7, 1, 12, 15, tzinfo=UTC),
            session_status=SessionStatus.ACTIVE,
            session_id=None,
        )


def test_token_validation_result_keeps_claims_separate_from_permissions() -> None:
    issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    result = TokenValidationResult(
        provider_subject="auth0|subject-10",
        issuer="https://tenant.auth0.com/",
        audience="https://api.erp.test",
        issued_at=issued_at,
        expires_at=issued_at + timedelta(minutes=15),
        email="admin@acme.test",
        claims={"roles": ["admin"], "scope": "openid profile email"},
    )

    assert result.provider_subject == "auth0|subject-10"
    assert result.claims["roles"] == ["admin"]
    assert not hasattr(result, "permissions")
