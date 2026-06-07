# Tasks: Architecture Foundation & Spec Definition

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1,800-2,600 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 docs/ADRs -> PR 2 backend scaffold -> PR 3 frontend scaffold -> PR 4 tests/CI/Flyway |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Canonical architecture docs and ADRs | PR 1 | Reviewable docs-only foundation. |
| 2 | Backend hexagonal scaffold and shared ports | PR 2 | Depends on PR 1 decisions. |
| 3 | Customer/invoice API and frontend feature skeletons | PR 3 | Depends on PR 2 structure. |
| 4 | PostgreSQL, Flyway, tests, CI | PR 4 | Verifies scaffold without full business implementation. |

## Phase 1: Architecture Foundation

- [x] 1.1 Update `docs/coding-standards.md` to remove Vertical Slice and define Hexagonal + DDD feature-folder rules.
- [x] 1.2 Rewrite `docs/bounded-context.md` with IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, HR and context relationships.
- [x] 1.3 Create `docs/adr/ADR-001-hexagonal-ddd.md` covering decision, alternatives, consequences, and rollback.
- [x] 1.4 Create `docs/cross-cutting/{unit-of-work,error-handling,logging,auth,fel,multi-tenancy}.md` with contracts and operational boundaries.
- [x] 1.5 Update `AGENTS.md` to point to canonical bounded contexts and route-prefix convention.

## Phase 2: Customer + Invoice Technical Tasks

- [x] 2.1 Create `backend/src/crm/{controllers,services,repositories,domain,schemas}/` for Customer flows from `openspec/specs/customer/spec.md` using `/crm/customers` routes.
- [x] 2.2 Create `backend/src/sales/{controllers,services,repositories,domain,schemas}/` for Invoice flows from `openspec/specs/invoice/spec.md` using `/sales/invoices` routes.
- [x] 2.3 Define `backend/src/shared/uow/` and repository ports for customer uniqueness, invoice posting, inventory/accounting coordination, and transaction rollback.
- [x] 2.4 Define `backend/src/shared/outbox/` plus FEL event contracts for `posted_pending_fel`, `fel_authorized`, `fel_failed`, and `credited`.
- [x] 2.5 Define `backend/src/shared/auth/` `AuthProvider` port with `fastapi-fullauth` adapter placeholder and OIDC migration notes.
- [x] 2.6 Create `backend/src/shared/fel/` `FelProvider` port and Infile adapter skeleton; no synchronous FEL posting.

## Phase 3: Scaffolding, Tooling, and Verification

- [ ] 3.1 Create backend package skeleton under `backend/src/` with `main.py`, `shared/config/`, dependency wiring, and empty FastAPI routers.
- [x] 3.2 Create `frontend/` Vite React TypeScript structure with `frontend/src/features/{customers,invoices}/{components,hooks,types,api}/`.
- [ ] 3.3 Add `docker-compose.yml` for PostgreSQL and environment variables consumed by backend config.
- [ ] 3.4 Add `migrations/sql/V1__base_schema.sql` for customers, contacts, invoices, invoice_lines, outbox, and auth seeds.
- [ ] 3.5 Add pytest/pytest-asyncio no-op tests for backend import, UoW contract, and route registration.
- [ ] 3.6 Add Vitest/React Testing Library no-op tests for customer and invoice feature modules.
- [ ] 3.7 Add `.github/workflows/ci.yml` running lint/type/test placeholders for backend and frontend.

## Phase 4: Deferred Follow-up Specs

- [ ] 4.1 Create a follow-up OpenSpec change for Inventory, Accounting, Purchasing, HR, Banking, Sales, and IAM detailed specs.
- [ ] 4.2 Keep current apply limited to foundation/scaffold; do not implement full business logic beyond contract skeletons.
