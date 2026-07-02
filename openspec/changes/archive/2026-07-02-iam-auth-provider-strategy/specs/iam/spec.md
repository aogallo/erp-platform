# Delta for IAM

## ADDED Requirements

### Requirement: Explicit Access Provisioning

IAM MUST allow access only through invitation or explicit admin/security assignment. Public self-registration MUST NOT create ERP access. Tenant membership SHALL be explicit; email domains MUST NOT grant access.

#### Scenario: Invite user into tenant

- GIVEN tenant A is active and an IAM admin invites `user@acme.test`
- WHEN the invite is accepted through provider login
- THEN IAM links the user only to the configured tenant membership

#### Scenario: Email domain does not imply tenant access

- GIVEN tenant A uses `acme.test` as an institutional domain
- WHEN `person@acme.test` authenticates without explicit tenant membership
- THEN IAM rejects access for tenant A

### Requirement: Local Authorization and Revocation Ownership

IAM MUST keep ERP roles, permissions, tenant memberships, user status, sessions, and authorization decisions local. Provider claims SHALL identify the subject but MUST NOT source ERP permissions. Local revocation MUST take effect immediately.

#### Scenario: Provider role claim ignored for ERP permission

- GIVEN a valid provider token includes role `admin`
- WHEN the principal is built for tenant A
- THEN IAM grants only locally stored permissions for that user and tenant

#### Scenario: Permission removed locally

- GIVEN U-10 no longer has `sales.invoice.post` locally
- WHEN U-10 calls the Sales posting endpoint with a valid token
- THEN authorization fails before Sales records side effects

#### Scenario: Disabled local user with valid token

- GIVEN user U-10 is disabled locally after receiving a valid provider token
- WHEN U-10 uses the token for an API request
- THEN IAM rejects it immediately

## MODIFIED Requirements

### Requirement: Users and Authentication Provider Boundary

The system MUST maintain tenant-scoped user identities and authenticate them through a provider-neutral OIDC boundary. Auth0 SHALL be first candidate. Provider SDK details MUST stay behind IAM infrastructure adapters and MUST NOT leak into domain objects or other contexts. A user SHALL include stable user ID, tenant, username or email, status, provider subject reference, and UTC audit timestamps.
(Previously: IAM preferred a self-hosted provider adapter with `fastapi-fullauth` as first candidate.)

#### Scenario: Register user through provider contract

- GIVEN tenant A is active
- WHEN an authorized IAM workflow provisions `admin@acme.test`
- THEN IAM stores only the local user, tenant assignment, and provider subject reference

#### Scenario: Provider swap preserves domain contract

- GIVEN IAM uses a different OIDC provider adapter
- WHEN a user authenticates successfully
- THEN IAM returns the same principal, tenant, and permission contract

#### Scenario: Disabled user cannot authenticate

- GIVEN user U-10 is disabled locally
- WHEN U-10 presents valid provider credentials or tokens
- THEN IAM rejects access and no ERP session is issued

### Requirement: Sessions and Principal Claims

IAM MUST validate provider access tokens and local session policy. Frontend clients SHALL obtain an ERP API audience access token using Authorization Code + PKCE and send `Authorization: Bearer <access_token>`. Validation SHALL check issuer, audience, signature, and expiry, then map claims to an ERP Principal with user ID, tenant ID, permissions or lookup reference, UTC issue/expiry timestamps, and session status.
(Previously: IAM issued and validated sessions generically through the provider boundary without the Auth0/OIDC access-token flow.)

#### Scenario: Start authenticated session

- GIVEN active tenant A and active user U-10 with tenant membership
- WHEN U-10 completes Authorization Code + PKCE for the ERP API audience
- THEN IAM validates the access token and returns principal claims with tenant A scope

#### Scenario: Expired session rejected

- GIVEN session S-10 expired at a UTC timestamp in the past
- WHEN a bounded context validates S-10
- THEN IAM rejects the session and no permission check succeeds

#### Scenario: Revoked session rejected

- GIVEN session S-11 was revoked locally by an authorized IAM user
- WHEN S-11 is used for an API request
- THEN IAM rejects the request even if the provider token has not expired
