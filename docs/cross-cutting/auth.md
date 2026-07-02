# Authentication and Authorization

## Contract

IAM owns local principals, roles, permissions, RBAC policies, tenant scope,
session policy, and revocation. Auth0 is the first authentication provider
candidate through a provider-neutral OIDC boundary. Business contexts consume a
local ERP principal and check permissions through the shared auth contract; they
do not consume provider SDKs, provider roles, or raw token claims.

```python
class AuthProvider(Protocol):
    async def principal_from_bearer(
        self, token: str, tenant_id: str | None = None
    ) -> Principal: ...

    def require_permission(self, principal: Principal, permission: str) -> None: ...
```

The implementation contract lives in `backend/src/shared/auth/contracts.py`.
Use junior-friendly names such as `contracts.py`, `repositories.py`, and
provider contracts; do not introduce `ports.py` for the auth boundary.

## Provider Boundary

- Auth0 is the first hosted OIDC provider candidate.
- Frontend clients use Authorization Code + PKCE to obtain an access token for
  the ERP API audience.
- API clients send the token as `Authorization: Bearer <access_token>`.
- FastAPI auth dependencies validate issuer, audience, signature, and expiry
  before IAM maps provider claims to a local ERP principal.
- Provider SDKs and provider-specific configuration stay inside infrastructure
  adapters such as `shared.auth.adapters.auth0` and `shared.auth.adapters.oidc`.
- Provider details MUST NOT leak into domain objects or business contexts.
- A later Keycloak or local provider adapter MUST preserve the same principal and
  permission contract.

## Operational Boundary

- Auth0 handles hosted login, password policy, MFA, password reset, provider
  sessions, SSO, and provider audit mechanics.
- ERP IAM remains authoritative for tenants, local users, tenant memberships,
  roles, permissions, local sessions, revocation, and authorization decisions.
- Public self-registration MUST NOT create ERP access. Access requires invitation
  or explicit admin/security assignment.
- Provider claims MAY identify the subject and email. Provider role or
  organization claims MUST NOT grant ERP permissions.
- Use RBAC as the default authorization model: users receive roles, roles receive
  permissions, and business contexts check permissions instead of hard-coding
  role names.
- Business contexts MUST NOT store passwords or provider session internals.
- Authorization failures are 403; authentication failures are 401.

## Frontend API Client Convention

- Shared Axios instance creation belongs in `frontend/src/lib/axiosClient.ts`.
- Shared TanStack Query client creation belongs in
  `frontend/src/lib/queryClient.ts`.
- IAM feature code MAY wrap the shared Axios factory to add auth behavior.
- The IAM API client MUST attach `Authorization: Bearer <access_token>` through
  an Axios request interceptor that reads token storage at request time.
- Query and mutation functions SHOULD use the shared IAM API client rather than
  calling `fetch` directly from React components.

## RBAC Rule

- IAM is the source of truth for roles and permissions.
- Context permissions SHOULD be named by bounded context and action, for example
  `crm.customer.read`, `crm.customer.write`, `sales.invoice.post`, and
  `accounting.journal-entry.read`.
- Controllers and services MUST check permissions through
  `AuthProvider.require_permission(...)` or an equivalent policy service.

## Revocation Rule

- Local revocation MUST take effect immediately, even when the provider access
  token has not expired.
- IAM MUST check local user status, tenant membership, local session status, and
  locally stored permissions on authenticated requests.
- Disabling a user, revoking a local session, removing tenant membership, or
  removing a permission MUST prevent the next protected action from succeeding.
