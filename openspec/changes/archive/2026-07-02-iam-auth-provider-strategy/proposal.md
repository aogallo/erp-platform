# Proposal: IAM Auth Provider Strategy

## Intent

Harden IAM authentication strategy: use Auth0 first while preserving a provider-neutral IAM boundary. The ERP avoids owning password policy, MFA, resets, lockout, SSO, session hardening, and provider audit mechanics, but remains authoritative for tenants, users, roles, permissions, authorization, and revocation.

## Scope

### In Scope
- Define Auth0/OIDC login with Authorization Code + PKCE and ERP API audience tokens.
- Preserve a swappable provider contract for Keycloak or a local adapter later.
- Require invitation or explicit admin/security assignment; no public self-registration.
- Keep ERP roles and permissions in the ERP database; provider claims map to an ERP Principal.
- Require explicit tenant configuration for institutional email; email domain alone must not grant access.
- Require immediate revocation through ERP session/revocation policy.

### Out of Scope
- Provider SDK integration, migrations, or Auth0 tenant setup.
- Public signup, social login, automatic tenant discovery, provider-managed ERP RBAC.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `iam`: Update provider, invitation, tenant mapping, principal validation, RBAC ownership, and revocation requirements.

## Approach

Specify IAM as a provider-neutral OIDC boundary with Auth0 first. Frontend obtains an access token through Authorization Code + PKCE for the ERP API audience and sends `Authorization: Bearer <access_token>`. FastAPI validates issuer, audience, signature, and expiry, then maps claims to an ERP Principal backed by local tenant/user/status/role/permission records. Revocation is local and authoritative.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/iam/spec.md` | Modified | Provider and auth/session deltas. |
| `docs/cross-cutting/auth.md` | Modified | Auth0-first OIDC guidance. |
| `docs/cross-cutting/multi-tenancy.md` | Modified | No email/domain-only tenant mapping. |
| `backend/src/shared/auth/` | Planned | Future adapter/principal contract. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Auth0 lock-in | Med | Keep OIDC/provider contract and local authorization. |
| Wrong invitation grants access | Med | Require explicit tenant/user/role assignment. |
| Token valid after removal | High | Check local revocation/status every request. |

## Rollback Plan

Revert IAM deltas and cross-cutting docs to existing self-hosted-first guidance. Specification only; no runtime data or provider configuration rollback is required.

## Dependencies

- Auth0 OIDC: hosted login, JWKS, issuer/audience validation, invitations.
- PyJWT or equivalent JWT validation plumbing in FastAPI during implementation.
- Local IAM tenant/user/role/permission/session/revocation model.

## Success Criteria

- [ ] IAM specs state Auth0 is first candidate without leaking provider details into domain contracts.
- [ ] Specs reject public self-registration and implicit email-domain access.
- [ ] Specs keep ERP RBAC local and provider-neutral.
- [ ] Specs require immediate revocation despite token expiry windows.
