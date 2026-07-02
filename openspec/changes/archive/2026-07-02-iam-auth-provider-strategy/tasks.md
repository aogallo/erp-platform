# Tasks: IAM Auth Provider Strategy

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650-900 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 contracts/settings → PR 2 backend adapters/IAM policy → PR 3 frontend/docs |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Shared auth contracts and typed settings | PR 1 | Independent foundation; tests included. |
| 2 | OIDC/Auth0 adapters and IAM local policy skeleton | PR 2 | Depends on PR 1; tests prove local authority. |
| 3 | Frontend token boundary and cross-cutting docs | PR 3 | Depends on PR 1 contracts and chosen backend flow. |

## Phase 1: Shared Contract Foundation

- [x] 1.1 RED: Add pytest coverage for `backend/src/shared/auth/contracts.py`: `Principal`, `AuthProvider.principal_from_bearer`, and `require_permission` contract expectations.
- [x] 1.2 GREEN: Create `backend/src/shared/auth/contracts.py` with provider-neutral principal, token validation, local permission, UTC timestamp, and session status shapes.
- [x] 1.3 RED: Add settings tests for `ERP_AUTH_ISSUER`, `ERP_AUTH_AUDIENCE`, `ERP_AUTH_JWKS_URL`, and session policy fields.
- [x] 1.4 GREEN: Update `backend/src/shared/config/settings.py` with typed OIDC/session settings and safe defaults.

## Phase 2: Backend Provider and IAM Policy

- [x] 2.1 RED: Add adapter tests for issuer, audience, signature, expiry, and claim extraction in `backend/src/shared/auth/adapters/oidc.py`.
- [x] 2.2 GREEN: Create `backend/src/shared/auth/adapters/oidc.py` as the provider-neutral JWT/JWKS validation skeleton.
- [x] 2.3 RED: Add Auth0 adapter tests proving Auth0 config wraps the OIDC adapter without leaking SDK/domain dependencies.
- [x] 2.4 GREEN: Create `backend/src/shared/auth/adapters/auth0.py` and update `backend/src/shared/auth/adapters/fastapi_fullauth.py` as a legacy/local candidate.
- [x] 2.5 RED: Add IAM policy tests for explicit tenant membership, disabled users, revoked sessions, removed permissions, and ignored provider role claims.
- [x] 2.6 GREEN: Create `backend/src/iam/` contracts/services/repository interfaces for tenants, users, memberships, roles, permissions, sessions, invitations, and local policy.

## Phase 3: Frontend Auth Boundary

- [x] 3.1 RED: Add Vitest coverage for `frontend/src/features/iam/` PKCE login setup, token storage boundary, and bearer-token API attachment.
- [x] 3.2 GREEN: Create `frontend/src/features/iam/` Auth0 PKCE adapter, token storage boundary, query/client auth header utilities, Zod schemas, and types.

## Phase 4: Documentation and Verification

- [x] 4.1 Update `docs/cross-cutting/auth.md` with Auth0-first OIDC, local RBAC ownership, no public self-registration, and immediate revocation rules.
- [x] 4.2 Update `docs/cross-cutting/multi-tenancy.md` with explicit tenant membership and no email-domain-derived access.
- [x] 4.3 Run `uv run pytest` and relevant Vitest checks when tooling exists; otherwise document unavailable tooling and verify tasks against IAM delta scenarios.
