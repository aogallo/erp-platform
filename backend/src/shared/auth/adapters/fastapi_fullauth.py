"""Placeholder adapter for the self-hosted `fastapi-fullauth` candidate.

No third-party dependency is imported in this scaffold PR. The future adapter
should translate fastapi-fullauth users, roles, permissions, and tenant scope
into the provider-neutral `Principal` contract.

Legacy/local-provider notes:
- Keep controllers and services dependent only on `AuthProvider`.
- Prefer the OIDC/Auth0 adapter for managed identity.
- Resolve roles, permissions, tenants, and revocation from local IAM state.
- Preserve context permission names such as `crm.customer.write` and
  `sales.invoice.post` to avoid changing business code during migration.
"""

from __future__ import annotations

from shared.auth.contracts import Principal


class FastApiFullAuthProvider:
    """Import-safe skeleton for the future fastapi-fullauth adapter."""

    async def principal_from_bearer(
        self, token: str, tenant_id: str | None = None
    ) -> Principal:
        raise NotImplementedError("fastapi-fullauth adapter is not wired yet")

    def require_permission(self, principal: Principal, permission: str) -> None:
        if permission not in principal.permissions:
            raise PermissionError(f"Missing required permission: {permission}")
