# Proposal: Database Persistence Foundation

## Intent

Define the shared PostgreSQL, Flyway, SQLAlchemy, and transaction-manager foundation before Accounting persistence work. The repo has persistence contracts but no ORM models, SQL migrations, Flyway config, or concrete async transaction boundary.

## Scope

### In Scope
- Flyway baseline for schemas: `iam`, `crm`, `sales`, `inventory`, `purchasing`, `accounting`, `banking`, `hr`.
- Conventions: UUID PKs, `pgcrypto`/`gen_random_uuid()`, UTC audit columns, actor audit columns, and explicit `tenant_id` rules.
- SQLAlchemy async engine/session setup, metadata strategy, and concrete transaction-manager boundary.
- RLS-ready design hooks without enabling PostgreSQL RLS in this slice.

### Out of Scope
- Business tables, seed data, first Accounting tables, or endpoint behavior.
- Schema-per-tenant implementation.
- Enabling RLS policies or operational RLS session variables.

## Capabilities

### New Capabilities
- `database-persistence-foundation`: Migration structure, schema baseline, UUID/audit/tenant conventions, SQLAlchemy async setup, and transaction-manager behavior.

### Modified Capabilities
- None.

## Approach

Use PostgreSQL schemas per bounded context plus `tenant_id` on tenant-scoped tables. Keep global/system catalogs tenantless only when explicitly global. Flyway owns reviewable SQL migrations and enables `pgcrypto` before UUID defaults. Shared SQLAlchemy async session infrastructure and transaction managers own commit/rollback; controllers and repositories must not commit directly.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/database-persistence-foundation/spec.md` | New | Persistence requirements. |
| `backend/src/shared/config/` | Modified | Database settings and URL handling. |
| `backend/src/shared/transactions/` | Modified | Concrete async transaction boundary. |
| `backend/src/shared/db/` | New | Engine, session factory, metadata conventions. |
| `backend/src/{context}/repositories/` | Modified | ORM metadata guidance. |
| `backend/migrations/` or `migrations/` | New | Flyway SQL migration location. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Schema drift between contexts | Med | Centralize conventions and table shape. |
| RLS later requires refactoring | Med | Reserve tenant columns and RLS-ready hooks now. |
| Flyway/SQLAlchemy metadata mismatch | Med | Require migrations as source of truth; ORM maps existing database. |

## Rollback Plan

Revert this OpenSpec change and any future implementation PR. In development, drop created schemas and Flyway history if needed; production rollback must use explicit forward migration scripts.

## Dependencies

- PostgreSQL with `pgcrypto` available.
- SQLAlchemy 2.x async driver stack and Flyway.
- Existing IAM tenant/principal contracts and transaction policy.

## Success Criteria

- [ ] Specs define Flyway baseline and bounded-context schemas without business tables.
- [ ] Specs require UUID defaults via `gen_random_uuid()` and audit columns on all tables.
- [ ] Specs distinguish tenant-scoped from explicitly global tables.
- [ ] Specs define async SQLAlchemy session setup and transaction-manager ownership.
- [ ] Specs prepare for RLS without enabling it in this slice.
