"""Local IAM authorization policy service."""

from __future__ import annotations

from datetime import UTC, datetime

from iam.contracts import UserStatus
from iam.repositories import IamPolicyRepository
from shared.auth.contracts import Principal, SessionStatus, TokenValidationResult


class LocalIamPolicyService:
    """Build principals from verified provider claims and local IAM policy."""

    def __init__(self, *, repository: IamPolicyRepository) -> None:
        self._repository = repository

    async def build_principal(
        self,
        *,
        token: TokenValidationResult,
        tenant_id: str,
        session_id: str,
        now: datetime | None = None,
    ) -> Principal:
        current_time = now or datetime.now(UTC)
        user = await self._repository.get_user_by_provider_subject(
            token.provider_subject
        )
        if user is None:
            raise PermissionError("Local user is not provisioned")
        if user.status is UserStatus.DISABLED:
            raise PermissionError("Local user is disabled")

        tenant = await self._repository.get_tenant(tenant_id)
        if tenant is None or not tenant.active:
            raise PermissionError("Tenant is not active")

        membership = await self._repository.get_tenant_membership(
            user_id=user.user_id, tenant_id=tenant_id
        )
        if membership is None or not membership.active:
            raise PermissionError("Tenant membership is not active")

        session = await self._repository.get_session(session_id)
        if session is None or session.user_id != user.user_id:
            raise PermissionError("Local session is not active")
        session_inactive = session.status is not SessionStatus.ACTIVE
        session_expired = session.expires_at <= current_time
        if session_inactive or session_expired:
            raise PermissionError("Local session is not active")

        permissions = await self._repository.list_permissions(
            user_id=user.user_id, tenant_id=tenant_id
        )
        return Principal(
            user_id=user.user_id,
            tenant_id=tenant_id,
            provider_subject=token.provider_subject,
            email=user.email,
            permissions=permissions,
            issued_at=token.issued_at,
            expires_at=token.expires_at,
            session_status=session.status,
            session_id=session.session_id,
        )
