# Multi-Tenancy

## Contract

Tenant scope comes from IAM and is passed to application services and repositories. Tenant isolation is a mandatory data-access invariant.

## Operational Boundary

- Every tenant-owned table MUST include tenant identity once persistence is introduced.
- Repositories MUST filter by tenant scope for reads and writes.
- Cross-tenant administrative actions require explicit IAM permissions and audit logging.
- Tenant IDs MUST be included in logs and outbox messages where applicable.
- Provider adapters MUST NOT infer tenant from global process state.
