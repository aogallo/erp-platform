# Apply Progress: Architecture Foundation & Spec Definition

## Mode

Standard. Strict TDD is disabled in `openspec/config.yaml` and no test runner is configured.

## Completed Tasks

- [x] 1.1 Updated `docs/coding-standards.md` to remove Vertical Slice and define Hexagonal + DDD feature-folder rules.
- [x] 1.2 Rewrote `docs/bounded-context.md` with IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, HR and context relationships.
- [x] 1.3 Created `docs/adr/ADR-001-hexagonal-ddd.md` covering decision, alternatives, consequences, and rollback.
- [x] 1.4 Created cross-cutting concern docs for Unit of Work, error handling, logging, auth, FEL, and multi-tenancy.
- [x] 1.5 Updated `AGENTS.md` to point to canonical bounded contexts and route-prefix convention.

## Workload / PR Boundary

- Mode: stacked PR slice
- Current work unit: PR 1 docs/ADRs
- Boundary: docs-only architecture foundation

## Deviations from Design

None. Backend/frontend scaffolding, migrations, CI, and tests were intentionally left for later PR slices.
