"""Placeholder adapter for the self-hosted `fastapi-fullauth` candidate.

No third-party dependency is imported in this scaffold PR. The future adapter
should translate fastapi-fullauth users, roles, permissions, and tenant scope
into the provider-neutral `Principal` contract.

OIDC migration notes:
- Keep controllers and services dependent only on `AuthProvider`.
- Add an OIDC/Auth0 adapter beside this module when managed identity is needed.
- Map OIDC subject, tenant claim, roles, and permissions into `Principal`.
- Preserve context permission names such as `crm.customer.write` and
  `sales.invoice.post` to avoid changing business code during migration.
"""

from __future__ import annotations

from shared.auth.ports import Principal


class FastApiFullAuthProvider:
    """Import-safe skeleton for the future fastapi-fullauth adapter."""

    async def authenticate(self, username: str, password: str) -> Principal:
        raise NotImplementedError("fastapi-fullauth adapter is not wired yet")

    def require_permission(self, principal: Principal, permission: str) -> None:
        if permission not in principal.permissions:
            raise PermissionError(f"Missing required permission: {permission}")
