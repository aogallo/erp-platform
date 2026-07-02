"""Repository interfaces for IAM local authorization state."""

from __future__ import annotations

from typing import Protocol

from iam.contracts import LocalSession, LocalUser, TenantMembership


class IamPolicyRepository(Protocol):
    """Read-only local policy data needed to build a request principal."""

    async def get_user_by_provider_subject(
        self, provider_subject: str
    ) -> LocalUser | None:
        """Return the local user linked to the verified provider subject."""

    async def get_tenant_membership(
        self, *, user_id: str, tenant_id: str
    ) -> TenantMembership | None:
        """Return explicit tenant membership for the local user."""

    async def get_session(self, session_id: str) -> LocalSession | None:
        """Return the local session used for immediate revocation checks."""

    async def list_permissions(
        self, *, user_id: str, tenant_id: str
    ) -> frozenset[str]:
        """Return locally stored permissions for the user and tenant."""
