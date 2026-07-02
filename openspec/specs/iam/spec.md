# IAM Specification

## Purpose

IAM defines tenant identity, authentication provider boundaries, local authorization, session policy, RBAC, tenant isolation, and auditability for ERP access control.

## Requirements

### Requirement: Tenant Management

The system MUST maintain tenants as the isolation boundary for all bounded contexts. Each tenant SHALL have a stable tenant ID, legal or display name, status, configuration metadata, and UTC audit timestamps. Tenant lifecycle changes MUST preserve historical data and MUST NOT expose one tenant's data to another tenant.

#### Scenario: Create tenant

- GIVEN an authorized platform principal
- WHEN the principal creates tenant "Acme Corp"
- THEN IAM creates a tenant with active status and UTC audit timestamps

#### Scenario: Disabled tenant blocks authentication

- GIVEN tenant A is disabled
- WHEN a user from tenant A attempts to start a session
- THEN IAM rejects authentication and no active session is issued

#### Scenario: Tenant identity does not leak data

- GIVEN tenant A and tenant B both have users with similar email addresses
- WHEN tenant A queries IAM users
- THEN only tenant A users are returned

### Requirement: Users and Authentication Provider Boundary

The system MUST maintain tenant-scoped user identities and authenticate them through a provider-neutral OIDC boundary. Auth0 SHALL be first candidate. Provider SDK details MUST stay behind IAM infrastructure adapters and MUST NOT leak into domain objects or other contexts. A user SHALL include stable user ID, tenant, username or email, status, provider subject reference, and UTC audit timestamps.

#### Scenario: Register user through provider contract

- GIVEN tenant A is active
- WHEN an authorized IAM workflow provisions `admin@acme.test`
- THEN IAM stores only the local user, tenant assignment, and provider subject reference

#### Scenario: Provider swap preserves domain contract

- GIVEN IAM uses a different OIDC provider adapter
- WHEN a user authenticates successfully
- THEN IAM returns the same principal, tenant, and permission contract

#### Scenario: Disabled user cannot authenticate

- GIVEN user U-10 is disabled
- WHEN U-10 presents valid provider credentials or tokens
- THEN IAM rejects access and no ERP session is issued

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

### Requirement: Roles and Permissions

The system MUST maintain tenant-scoped roles and permissions for RBAC authorization. Permissions SHALL represent actions or capabilities, roles SHALL aggregate permissions, and users SHALL receive roles within a tenant scope. Business contexts MUST check permissions and MUST NOT hard-code roles in business rules.

#### Scenario: Create role with permissions

- GIVEN permissions "hr.payroll.approve" and "hr.payroll.read" exist for tenant A
- WHEN an authorized IAM user creates role "Payroll Manager"
- THEN IAM stores the role with those permissions for tenant A

#### Scenario: Assign role to user

- GIVEN user U-10 and role R-10 belong to tenant A
- WHEN an authorized IAM user assigns R-10 to U-10
- THEN U-10 receives the role permissions within tenant A

#### Scenario: Cross-tenant role assignment rejected

- GIVEN user U-10 belongs to tenant A and role R-20 belongs to tenant B
- WHEN IAM attempts to assign R-20 to U-10
- THEN IAM rejects the assignment without exposing tenant B role details

### Requirement: Sessions and Principal Claims

IAM MUST validate provider access tokens and local session policy. Frontend clients SHALL obtain an ERP API audience access token using Authorization Code + PKCE and send `Authorization: Bearer <access_token>`. Validation SHALL check issuer, audience, signature, and expiry, then resolve the validated subject to a local ERP Principal through explicit tenant membership or a local lookup reference. Permissions MUST come only from IAM state, never from provider token claims.

#### Scenario: Start authenticated session

- GIVEN active tenant A and active user U-10 with tenant membership
- WHEN U-10 completes Authorization Code + PKCE for the ERP API audience
- THEN IAM validates the access token subject and returns a local ERP Principal with tenant A membership and permissions from IAM state

#### Scenario: Expired session rejected

- GIVEN session S-10 expired at a UTC timestamp in the past
- WHEN a bounded context validates S-10
- THEN IAM rejects the session and no permission check succeeds

#### Scenario: Revoked session rejected

- GIVEN session S-11 was revoked locally by an authorized IAM user
- WHEN S-11 is used for an API request
- THEN IAM rejects the request even if the provider token has not expired

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

### Requirement: RBAC Checks for Bounded Contexts

IAM MUST expose an authorization contract that bounded contexts can use to evaluate permissions with principal and tenant scope. Context services own business authorization points, while IAM owns identity, role, permission, and session policy. Authorization failures MUST prevent side effects in the requesting context.

#### Scenario: HR payroll approval permission granted

- GIVEN principal P-10 has permission "hr.payroll.approve" in tenant A
- WHEN HR checks authorization for payroll approval in tenant A
- THEN IAM authorization succeeds and HR may continue its business validation

#### Scenario: Missing permission blocks action

- GIVEN principal P-10 lacks permission "banking.payment.approve"
- WHEN Banking checks authorization for payment approval
- THEN IAM authorization fails and Banking records no payment or accounting handoff

#### Scenario: Business context checks permissions, not roles

- GIVEN role "Admin" includes permission "accounting.report.read"
- WHEN Accounting authorizes report access
- THEN Accounting checks the permission result and does not branch on the role name

### Requirement: Tenant Isolation Enforcement

IAM MUST provide tenant scope to every authenticated request and every bounded context MUST apply that scope to commands and queries. IAM MUST reject attempts to use a principal outside its tenant unless an explicit platform-level tenant administration capability is present. Cross-context handoffs MUST include tenant ID and MUST be processed only inside that tenant boundary.

#### Scenario: Cross-tenant command rejected

- GIVEN principal P-10 is scoped to tenant A
- WHEN P-10 submits a command against tenant B data
- THEN IAM or the receiving context rejects the command before side effects occur

#### Scenario: Cross-context handoff includes tenant

- GIVEN HR sends payroll payable obligations to Accounting
- WHEN Accounting receives the handoff
- THEN the handoff includes tenant ID and Accounting records data only for that tenant

#### Scenario: Platform-level tenant administration is explicit

- GIVEN principal P-20 has a platform tenant administration permission
- WHEN P-20 disables tenant A
- THEN IAM records the action with UTC audit timestamp and does not grant P-20 business-context permissions by default

### Requirement: Migration-Safe Abstractions and Auditability

IAM MUST keep authentication provider, token, password, and session storage details behind migration-safe ports and adapters. Other bounded contexts SHALL depend only on IAM principal, authorization, and tenant-scope contracts. IAM MUST preserve audit records for identity, role, permission, session, and tenant administration changes with actor, tenant, UTC timestamp, action, and target reference.

#### Scenario: Replace authentication adapter without context changes

- GIVEN HR, Sales, Accounting, Banking, Inventory, and Purchasing use the IAM principal contract
- WHEN IAM replaces the underlying authentication provider adapter
- THEN those contexts require no domain model changes and continue receiving equivalent principal data

#### Scenario: Audit role permission change

- GIVEN role R-10 exists in tenant A
- WHEN an authorized IAM user adds permission "sales.invoice.post" to R-10
- THEN IAM records the actor, tenant, role, permission, and UTC timestamp in the audit trail

#### Scenario: Provider-specific field not exposed downstream

- GIVEN the authentication provider returns proprietary token metadata
- WHEN IAM validates a session for a bounded context
- THEN IAM maps it to the stable principal contract and does not expose provider-specific fields
