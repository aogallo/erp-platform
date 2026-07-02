# Multi-Tenancy

## Contract

Tenant scope comes from IAM and is passed to application services and repositories. Tenant isolation is a mandatory data-access invariant.

Tenant access is explicit. A user belongs to a tenant only when IAM has an active
tenant membership created by invitation or by explicit admin/security assignment.
Email domains are tenant metadata only; they do not grant access.

## Operational Boundary

- Every tenant-owned table MUST include tenant identity once persistence is introduced.
- Repositories MUST filter by tenant scope for reads and writes.
- Cross-tenant administrative actions require explicit IAM permissions and audit logging.
- Tenant IDs MUST be included in logs and outbox messages where applicable.
- Provider adapters MUST NOT infer tenant from global process state.
- Provider adapters MUST NOT infer tenant access from an email domain,
  organization claim, or provider role claim.
- Institutional email domains MAY help route invitations or display tenant
  metadata, but IAM MUST still require an active tenant membership before access
  is granted.
- When a user belongs to multiple tenants, tenant selection MUST be explicit in
  the request flow or session context before bounded-context services run.
