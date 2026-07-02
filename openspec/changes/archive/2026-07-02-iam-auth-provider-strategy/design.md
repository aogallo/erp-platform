# Design: IAM Auth Provider Strategy

## Technical Approach

Replace the current self-hosted-first auth contract with an Auth0-first, OIDC-compatible boundary while keeping ERP authorization local. Auth0 handles login, MFA, password policy, hosted sessions, and token issuance. FastAPI validates ERP API audience access tokens and maps provider claims to a local `Principal` backed by IAM tenant, user, role, permission, and session policy records. No business context consumes provider SDKs or provider RBAC.

The repo currently has only a shared auth interface scaffold and no `backend/src/iam/` implementation, so this design introduces clearer contracts before runtime wiring.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Provider boundary | Rename/reshape `AuthProvider` around OIDC token validation and permission checks, with Auth0 as first adapter. | Keep username/password `authenticate`; couple controllers to Auth0 SDK. | Authorization Code + PKCE produces bearer access tokens; SDK coupling would violate the provider-neutral boundary. |
| Local authority | Store tenant membership, user status, roles, permissions, sessions, and revocation locally. | Trust provider roles/organizations; infer tenant from email domain. | Specs require ERP-owned RBAC and immediate revocation; institutional email is metadata, not access. |
| Principal shape | Extend `Principal` with local `user_id`, `tenant_id`, provider subject, permissions, issued/expiry UTC timestamps, and session status/reference. | Put provider claims directly on domain objects. | Keeps bounded contexts stable and prevents provider details leaking into domain logic. |
| Revocation | Check local status/session/permission policy on every authenticated request. | Rely only on JWT `exp`; use long-lived stateless authorization. | Disabled users and removed permissions must fail immediately even with a valid provider token. |

## Data Flow

```text
Browser ── Authorization Code + PKCE ──→ Auth0
Browser ←──── ERP API audience access token ─── Auth0
Browser ── Authorization: Bearer token ──→ FastAPI dependency
FastAPI ── validate iss/aud/sig/exp/JWKS ──→ OidcAuthProvider
OidcAuthProvider ── subject/email lookup ──→ IAM local repositories
IAM local policy ── active user + tenant + session + permissions ──→ Principal
Bounded context ── require_permission(principal, permission) ──→ allowed/403
```

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/src/shared/auth/contracts.py` | Create/Rename | Define token validation, local principal construction, and `require_permission` contracts with junior-friendly naming. |
| `backend/src/shared/auth/adapters/fastapi_fullauth.py` | Modify | Mark as legacy/local candidate and align placeholder docs with the OIDC-neutral contract. |
| `backend/src/shared/auth/adapters/oidc.py` | Create | Provider-neutral JWT/JWKS validation skeleton for issuer, audience, signature, expiry, and claim extraction. |
| `backend/src/shared/auth/adapters/auth0.py` | Create | Auth0-specific configuration defaults over the generic OIDC adapter, with no domain imports of Auth0 SDKs. |
| `backend/src/iam/` | Create | IAM bounded-context contracts for users, tenants, memberships, roles, permissions, sessions, invitations, and local policy services. |
| `backend/src/shared/config/settings.py` | Modify | Add typed `ERP_AUTH_ISSUER`, `ERP_AUTH_AUDIENCE`, `ERP_AUTH_JWKS_URL`, and session policy settings. |
| `frontend/src/features/iam/` | Create | Auth0 PKCE login/token adapter, token storage boundary, and API bearer-token attachment utilities. |
| `docs/cross-cutting/auth.md` | Modify | Document Auth0-first OIDC, local RBAC ownership, no self-registration, and revocation policy. |
| `docs/cross-cutting/multi-tenancy.md` | Modify | Document explicit tenant membership and no email-domain-derived access. |

## Interfaces / Contracts

```python
class AuthProvider(Protocol):
    async def principal_from_bearer(self, token: str, tenant_id: str | None) -> Principal: ...
    def require_permission(self, principal: Principal, permission: str) -> None: ...
```

`principal_from_bearer` MUST validate OIDC token cryptography before local lookup. Provider claims MAY supply subject and email; ERP MUST resolve local tenant membership, user status, session status, and permissions from IAM storage.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | JWT claim mapping, permission rejection, disabled user/session revocation, provider roles ignored. | pytest with fake OIDC validator and in-memory IAM repository contracts/fakes. |
| Integration | FastAPI dependency returns `Principal` or 401/403; settings load auth config. | TestClient with test JWKS/token fixtures once tooling exists. |
| E2E | Auth0 PKCE browser login to protected ERP API. | Deferred until frontend auth shell and test environment exist. |

## Migration / Rollout

No data migration in this spec-only change. Implementation should land behind configuration: add OIDC settings, introduce IAM local tables via Flyway, seed no implicit users, then enable protected routes per bounded context. Existing scaffold endpoints remain unauthenticated until each implementation phase wires IAM dependencies.

## Open Questions

- [ ] Which local session identifier should tie an OIDC access token to ERP revocation state: token `jti`, provider subject plus issued-at, or ERP-issued session record?
- [ ] Should tenant selection be explicit in the route/header when a user belongs to multiple tenants?
