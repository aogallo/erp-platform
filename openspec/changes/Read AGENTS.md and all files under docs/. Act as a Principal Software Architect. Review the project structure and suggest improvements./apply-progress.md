# Apply Progress: Architecture Foundation & Spec Definition

## Mode

Standard for the current chained PR slices. `openspec/config.yaml` declares `strict_tdd: true` as the project policy, but test runners are not installed yet because backend tooling is planned for a later slice. Pytest, Ruff, and Pyright remain planned for the tooling slice; this PR keeps code import-safe with the Python standard library only.

## Completed Tasks

- [x] 1.1 Updated `docs/coding-standards.md` to remove Vertical Slice and define Hexagonal + DDD feature-folder rules.
- [x] 1.2 Rewrote `docs/bounded-context.md` with IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, HR and context relationships.
- [x] 1.3 Created `docs/adr/ADR-001-hexagonal-ddd.md` covering decision, alternatives, consequences, and rollback.
- [x] 1.4 Created cross-cutting concern docs for Unit of Work, error handling, logging, auth, FEL, and multi-tenancy.
- [x] 1.5 Updated `AGENTS.md` to point to canonical bounded contexts and route-prefix convention.
- [x] 2.1 Created `src/crm/{controllers,services,repositories,domain,schemas}/` for Customer flows with `/crm/customers` route contracts.
- [x] 2.2 Created `src/sales/{controllers,services,repositories,domain,schemas}/` for Invoice flows with `/sales/invoices` route contracts.
- [x] 2.3 Defined `src/shared/uow/` Unit of Work and coordination ports for customer uniqueness, invoice posting, inventory/accounting coordination, and rollback.
- [x] 2.4 Defined `src/shared/outbox/` and FEL lifecycle event contracts for `posted_pending_fel`, `fel_authorized`, `fel_failed`, and `credited`.
- [x] 2.5 Defined `src/shared/auth/` `AuthProvider`, `Principal`, a `fastapi-fullauth` adapter placeholder, and OIDC migration notes.
- [x] 2.6 Created `src/shared/fel/` `FelProvider`, `FelResult`, and an Infile adapter skeleton that is explicitly asynchronous/outbox-driven.

## Files Changed in PR 2

- `src/__init__.py` — backend package marker.
- `src/crm/controllers/routes.py` — CRM customer route constants for `/crm/customers` endpoints.
- `src/crm/domain/customer.py` — Customer, Contact, and CustomerStatus domain primitives.
- `src/crm/repositories/ports.py` — CustomerRepository persistence contract, including tax ID uniqueness and contact operations.
- `src/crm/schemas/customer.py` — import-safe customer request/response dataclass placeholders.
- `src/crm/services/customers.py` — CustomerService application service contract.
- `src/sales/controllers/routes.py` — Sales invoice route constants for `/sales/invoices` endpoints.
- `src/sales/domain/invoice.py` — Invoice, InvoiceLine, and InvoiceStatus domain primitives.
- `src/sales/repositories/ports.py` — InvoiceRepository persistence contract for invoice lifecycle transitions.
- `src/sales/schemas/invoice.py` — import-safe invoice request/response dataclass placeholders.
- `src/sales/services/invoices.py` — InvoiceService application service contract.
- `src/shared/uow/ports.py` — UnitOfWork plus customer lookup, inventory coordination, and accounting coordination ports.
- `src/shared/outbox/events.py` — provider-neutral FEL lifecycle outbox event contracts.
- `src/shared/outbox/ports.py` — OutboxRepository contract.
- `src/shared/auth/ports.py` — Principal and AuthProvider contracts.
- `src/shared/auth/adapters/fastapi_fullauth.py` — fastapi-fullauth adapter placeholder and OIDC migration notes.
- `src/shared/fel/ports.py` — provider-neutral FEL provider contract and result model.
- `src/shared/fel/adapters/infile.py` — Infile adapter skeleton with no SDK import and no synchronous posting.
- Package `__init__.py` files under `src/crm`, `src/sales`, and `src/shared` — keep scaffold importable and tracked.

## Workload / PR Boundary

- Mode: stacked PR slice
- Current work unit: PR 2 backend scaffold/shared ports
- Boundary: starts after merged PR 1 docs/ADRs; ends with backend package/module scaffold and shared ports only. Frontend, migrations, Docker Compose, CI, dependency installation, and full business implementations remain out of scope.

## Deviations from Design

None for the assigned PR 2 slice. FastAPI/Pydantic/SQLAlchemy classes were intentionally not imported or wired because dependency/tooling setup belongs to a later slice; import-safe stdlib dataclasses and Protocols document the intended contracts until tooling exists.

## Issues Found

- `openspec/config.yaml` has `strict_tdd: true`, but backend test tooling is still marked planned and no runner is installed in this slice. Standard Mode was used per the PR 2 instruction.

## Remaining Tasks

- [ ] 3.1 Create backend package skeleton under `src/` with `main.py`, `shared/config/`, dependency wiring, and empty FastAPI routers.
- [ ] 3.2 Create `frontend/` Vite React TypeScript structure with `frontend/src/features/{customers,invoices}/{components,hooks,types,api}/`.
- [ ] 3.3 Add `docker-compose.yml` for PostgreSQL and environment variables consumed by backend config.
- [ ] 3.4 Add `migrations/sql/V1__base_schema.sql` for customers, contacts, invoices, invoice_lines, outbox, and auth seeds.
- [ ] 3.5 Add pytest/pytest-asyncio no-op tests for backend import, UoW contract, and route registration.
- [ ] 3.6 Add Vitest/React Testing Library no-op tests for customer and invoice feature modules.
- [ ] 3.7 Add `.github/workflows/ci.yml` running lint/type/test placeholders for backend and frontend.
- [ ] 4.1 Create a follow-up OpenSpec change for Inventory, Accounting, Purchasing, HR, Banking, Sales, and IAM detailed specs.
- [ ] 4.2 Keep current apply limited to foundation/scaffold; do not implement full business logic beyond contract skeletons.
