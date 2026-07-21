# Database Persistence Foundation Specification

## Purpose

Define the persistence baseline for PostgreSQL, Flyway, SQLAlchemy, and transaction-manager behavior before business tables are introduced.

## Requirements

### Requirement: Bounded-Context Schema Baseline

The system MUST provide a Flyway-managed PostgreSQL baseline for schemas `iam`, `crm`, `sales`, `inventory`, `purchasing`, `accounting`, `banking`, and `hr`. This slice MUST NOT create business tables, seed business data, or implement schema-per-tenant isolation.

#### Scenario: Create context schemas only

- GIVEN an empty application database
- WHEN the baseline migration runs
- THEN the listed bounded-context schemas exist
- AND no CRM, Sales, Accounting, Banking, Inventory, Purchasing, HR, or IAM business tables are created

#### Scenario: Additional schema rejected from baseline scope

- GIVEN this persistence foundation change
- WHEN a migration proposes a business or tenant schema outside the listed context schemas
- THEN review MUST reject it as out of scope for this slice

### Requirement: SQL Migration Source of Truth

Flyway SQL migrations MUST be reviewable and versioned as the database source of truth. Automatic migration generation MUST NOT be used. SQLAlchemy mappings MUST follow the committed SQL schema, not define independent database shape.

#### Scenario: Reviewable SQL migration accepted

- GIVEN a persistence change requires database structure
- WHEN the change is prepared
- THEN it includes explicit Flyway SQL migration files for review

#### Scenario: ORM-first migration rejected

- GIVEN SQLAlchemy model changes imply new database structure
- WHEN no matching committed SQL migration exists
- THEN the change MUST be rejected as schema drift risk

### Requirement: Application Table Conventions

All future application tables MUST use UUID primary keys with database defaults from `pgcrypto` `gen_random_uuid()`. Application tables MUST include UTC audit columns `created_at`, `updated_at`, `created_by`, and `updated_by`; `created_by` MUST be non-null for application-created records and `updated_by` MAY be nullable initially.

#### Scenario: UUID and audit shape required

- GIVEN a future application table migration
- WHEN reviewers inspect the table definition
- THEN the primary key uses UUID with `gen_random_uuid()` default
- AND required audit columns are present with UTC timestamp semantics

#### Scenario: Missing creation actor rejected

- GIVEN a future application-created record table
- WHEN `created_by` is nullable or absent
- THEN the migration MUST be rejected until creation actor auditing is enforced

### Requirement: Tenant Scope and RLS Readiness

Tenant-scoped tables MUST include `tenant_id`. Tenantless tables MAY exist only when explicitly global/system catalogs. The foundation MUST prepare for Row Level Security through compatible table conventions and session hooks, but MUST NOT enable RLS policies in this slice.

#### Scenario: Tenant-owned table includes tenant ID

- GIVEN a future tenant-owned table
- WHEN its migration is reviewed
- THEN it includes `tenant_id` suitable for repository filtering and future RLS policy use

#### Scenario: RLS not enabled yet

- GIVEN the baseline migration has run
- WHEN database policies are inspected
- THEN no application table has RLS enabled by this slice
- AND conventions remain compatible with enabling RLS later

### Requirement: Async SQLAlchemy and Transaction Boundary

The system MUST provide shared async SQLAlchemy engine/session infrastructure. A transaction manager MUST own transaction commit and rollback boundaries; controllers, services outside the transaction boundary, and repositories MUST NOT call raw session commits.

#### Scenario: Successful transaction manager commits once

- GIVEN an application service completes local persistence work through repositories
- WHEN the transaction manager commits
- THEN all local changes are committed through the managed transaction boundary

#### Scenario: Repository raw commit prohibited

- GIVEN repository code receives a SQLAlchemy session
- WHEN it persists or reads data
- THEN it MUST NOT call `session.commit()` directly
- AND rollback behavior remains owned by the transaction manager
