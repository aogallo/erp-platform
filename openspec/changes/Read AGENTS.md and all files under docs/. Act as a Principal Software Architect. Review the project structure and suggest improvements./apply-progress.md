# Apply Progress: Architecture Foundation & Spec Definition

## Mode

PRs 1-3 used Standard Mode because dependency manifests and test runners were not installed yet. PR4 runs in Strict TDD Mode where possible by creating the runner/tooling harness first; tasks that create the runner itself have documented non-runnable RED states before dependencies existed.

## Completed Tasks

- [x] 1.1 Updated `docs/coding-standards.md` to remove Vertical Slice and define Hexagonal + DDD feature-folder rules.
- [x] 1.2 Rewrote `docs/bounded-context.md` with IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, HR and context relationships.
- [x] 1.3 Created `docs/adr/ADR-001-hexagonal-ddd.md` covering decision, alternatives, consequences, and rollback.
- [x] 1.4 Created cross-cutting concern docs for Unit of Work, error handling, logging, auth, FEL, and multi-tenancy.
- [x] 1.5 Updated `AGENTS.md` to point to canonical bounded contexts and route-prefix convention.
- [x] 2.1 Created `backend/src/crm/{controllers,services,repositories,domain,schemas}/` for Customer flows with `/crm/customers` route contracts.
- [x] 2.2 Created `backend/src/sales/{controllers,services,repositories,domain,schemas}/` for Invoice flows with `/sales/invoices` route contracts.
- [x] 2.3 Defined `backend/src/shared/uow/` Unit of Work and coordination ports for customer uniqueness, invoice posting, inventory/accounting coordination, and rollback.
- [x] 2.4 Defined `backend/src/shared/outbox/` and FEL lifecycle event contracts for `posted_pending_fel`, `fel_authorized`, `fel_failed`, and `credited`.
- [x] 2.5 Defined `backend/src/shared/auth/` `AuthProvider`, `Principal`, a `fastapi-fullauth` adapter placeholder, and OIDC migration notes.
- [x] 2.6 Created `backend/src/shared/fel/` `FelProvider`, `FelResult`, and an Infile adapter skeleton that is explicitly asynchronous/outbox-driven.
- [x] 3.1 Created backend FastAPI application factory, typed config, dependency wiring, and empty CRM/Sales routers.
- [x] 3.2 Created `frontend/` Vite React TypeScript structure with customer and invoice feature modules.
- [x] 3.3 Added Docker Compose PostgreSQL service and `.env.example` variables consumed by backend config.
- [x] 3.4 Added Flyway base SQL migration for tenants, auth seeds, customers, contacts, invoices, invoice lines, and outbox.
- [x] 3.5 Added backend pytest/pytest-asyncio scaffold tests for imports, UoW contract, route registration, and config.
- [x] 3.6 Added Vitest/React Testing Library scaffold tests for customer and invoice feature modules.
- [x] 3.7 Added GitHub Actions CI for backend and frontend lint/type/test commands.
- [x] 4.1 Created `openspec/changes/defer-detailed-module-specs/` as the follow-up OpenSpec change for Inventory, Accounting, Purchasing, HR, Banking, Sales, and IAM detailed specs.
- [x] 4.2 Kept this apply limited to planning/foundation artifacts; no business logic, executable behavior, migrations, or detailed module specs were added in this slice.

## Files Changed in PR 2

- `backend/src/__init__.py` — backend package marker.
- `backend/src/crm/controllers/routes.py` — CRM customer route constants for `/crm/customers` endpoints.
- `backend/src/crm/domain/customer.py` — Customer, Contact, and CustomerStatus domain primitives.
- `backend/src/crm/repositories/ports.py` — CustomerRepository persistence contract, including tax ID uniqueness and contact operations.
- `backend/src/crm/schemas/customer.py` — import-safe customer request/response dataclass placeholders.
- `backend/src/crm/services/customers.py` — CustomerService application service contract.
- `backend/src/sales/controllers/routes.py` — Sales invoice route constants for `/sales/invoices` endpoints.
- `backend/src/sales/domain/invoice.py` — Invoice, InvoiceLine, and InvoiceStatus domain primitives.
- `backend/src/sales/repositories/ports.py` — InvoiceRepository persistence contract for invoice lifecycle transitions.
- `backend/src/sales/schemas/invoice.py` — import-safe invoice request/response dataclass placeholders.
- `backend/src/sales/services/invoices.py` — InvoiceService application service contract.
- `backend/src/shared/uow/ports.py` — UnitOfWork plus customer lookup, inventory coordination, and accounting coordination ports.
- `backend/src/shared/outbox/events.py` — provider-neutral FEL lifecycle outbox event contracts.
- `backend/src/shared/outbox/ports.py` — OutboxRepository contract.
- `backend/src/shared/auth/ports.py` — Principal and AuthProvider contracts.
- `backend/src/shared/auth/adapters/fastapi_fullauth.py` — fastapi-fullauth adapter placeholder and OIDC migration notes.
- `backend/src/shared/fel/ports.py` — provider-neutral FEL provider contract and result model.
- `backend/src/shared/fel/adapters/infile.py` — Infile adapter skeleton with no SDK import and no synchronous posting.
- Package `__init__.py` files under `backend/src/crm`, `backend/src/sales`, and `backend/src/shared` — keep scaffold importable and tracked.

## Workload / PR Boundary

- Mode: stacked PR slice
- Current work unit: PR 2 backend scaffold/shared ports
- Boundary: starts after merged PR 1 docs/ADRs; ends with backend package/module scaffold and shared ports only. Frontend, migrations, Docker Compose, CI, dependency installation, and full business implementations remain out of scope.

## Deviations from Design

None for the assigned PR 2 slice. FastAPI/Pydantic/SQLAlchemy classes were intentionally not imported or wired because dependency/tooling setup belongs to a later slice; import-safe stdlib dataclasses and Protocols document the intended contracts until tooling exists.

## Issues Found

- `openspec/config.yaml` has `strict_tdd: true`, but backend/frontend test tooling is still marked planned and no runner is installed in this slice. Standard Mode was used for scaffold-only PRs.

## Files Changed in PR 3

- `backend/src/` — moved backend scaffold from root `src/` to `backend/src/` to preserve backend/frontend separation.
- `backend/src/crm/services/customers.py` — imports `Page` directly from `shared.pagination` instead of through schemas.
- `backend/src/crm/schemas/customer.py` — no longer imports or re-exports shared pagination.
- `frontend/src/shared/pagination.ts` — shared frontend pagination type.
- `frontend/src/features/customers/{api,components,hooks,schemas,types}/` — Customer feature scaffold aligned to `/crm/customers`.
- `frontend/src/features/invoices/{api,components,hooks,schemas,types}/` — Invoice feature scaffold aligned to `/sales/invoices`.

## PR 3 Boundary

- Mode: stacked PR slice
- Current work unit: PR 3 frontend scaffold + backend layout correction
- Boundary: frontend feature scaffold and backend `backend/src/` relocation only. No package installation, Vite config, Docker, migrations, CI, or full UI implementation.

## Remaining Tasks

- [x] 3.1 Create backend package skeleton under `backend/src/` with `main.py`, `shared/config/`, dependency wiring, and empty FastAPI routers.
- [x] 3.2 Create `frontend/` Vite React TypeScript structure with `frontend/src/features/{customers,invoices}/{components,hooks,types,api}/`.
- [x] 3.3 Add `docker-compose.yml` for PostgreSQL and environment variables consumed by backend config.
- [x] 3.4 Add `migrations/sql/V1__base_schema.sql` for customers, contacts, invoices, invoice_lines, outbox, and auth seeds.
- [x] 3.5 Add pytest/pytest-asyncio no-op tests for backend import, UoW contract, and route registration.
- [x] 3.6 Add Vitest/React Testing Library no-op tests for customer and invoice feature modules.
- [x] 3.7 Add `.github/workflows/ci.yml` running lint/type/test placeholders for backend and frontend.
- [x] 4.1 Create a follow-up OpenSpec change for Inventory, Accounting, Purchasing, HR, Banking, Sales, and IAM detailed specs.
- [x] 4.2 Keep current apply limited to foundation/scaffold; do not implement full business logic beyond contract skeletons.

## Files Changed in PR 4

- `pyproject.toml` — backend dependency and tooling manifest for FastAPI, pytest, pytest-asyncio, Ruff, and Pyright.
- `backend/src/main.py` — FastAPI application factory and route registration state.
- `backend/src/shared/config/{__init__.py,settings.py}` — typed environment-backed backend settings.
- `backend/src/crm/controllers/routes.py`, `backend/src/sales/controllers/routes.py` — empty FastAPI routers for bounded-context route prefixes.
- `backend/tests/test_app_scaffold.py`, `backend/tests/test_uow_contract.py` — backend scaffold contract tests.
- `docker-compose.yml`, `.env.example` — local PostgreSQL service and backend environment contract.
- `migrations/sql/V1__base_schema.sql` — reviewable Flyway base schema and auth seeds.
- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/vitest.setup.ts`, `frontend/eslint.config.js` — frontend test/type/lint harness.
- `frontend/src/features/{customers,invoices}/components/*.test.tsx` — customer and invoice feature scaffold tests.
- `.github/workflows/ci.yml` — CI jobs for backend and frontend lint/type/test placeholders.
- `.gitignore` — local environment, Python cache, and frontend build/test artifact ignores.
- `uv.lock` — backend dependency lockfile for reproducible `uv sync --locked --dev` installs.
- `frontend/package-lock.json` — frontend dependency lockfile for reproducible `npm ci` installs.

## TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 3.1 | `backend/tests/test_app_scaffold.py` | Backend unit/API scaffold | N/A (runner created in PR4); warning-fix baseline `uv run pytest backend/tests/test_app_scaffold.py` passed 3/3 before route-test refactor | ✅ Written first; warning-fix RED first failed because `httpx2` was missing for `TestClient`, then failed with `404 != 501` after adding the dev test dependency | ✅ `uv run pytest backend/tests/test_app_scaffold.py` passed after real scaffold route handlers were added | ✅ Covered actual HTTP behavior for both `/crm/customers` and `/sales/invoices`, not internal app state | ✅ Removed `app.state.registered_router_prefixes` tracking from `main.py` |
| 3.3 | `backend/tests/test_app_scaffold.py` | Backend unit/config | N/A (new config) | ✅ Written first against `Settings.from_env()` before config existed | ✅ Backend pytest passed after `.env.example`, Docker env names, and settings implementation | ✅ Tested non-default host, port, DB, user, password | ✅ Centralized env reads in `shared.config` |
| 3.4 | `migrations/sql/V1__base_schema.sql`, `docker-compose.yml`, `.github/workflows/ci.yml` | Flyway migration validation | N/A (Flyway runner added in warning-fix pass) | ✅ `docker compose run --rm flyway` failed before the fix with `no such service: flyway` | ✅ Added a Docker Compose Flyway service and CI job that runs `docker compose up -d postgres` followed by `docker compose run --rm flyway` against PostgreSQL | ✅ Local `docker compose config` validates PostgreSQL + Flyway wiring; full local Flyway execution is blocked because the Docker daemon is not running | ✅ Kept Flyway isolated to tooling/CI and did not change migration SQL semantics |
| 3.5 | `backend/tests/test_app_scaffold.py`, `backend/tests/test_uow_contract.py` | Backend unit/contract | N/A (runner created in PR4) | ✅ Tests added before implementation; first backend run failed on missing `main` | ✅ `uv run pytest` passed: 5/5 | ✅ Import, route registration, settings, UoW method presence, and async method checks | ✅ Fixed settings default constants for slotted dataclass behavior |
| 3.6 | `frontend/src/features/customers/components/CustomerListPlaceholder.test.tsx`, `frontend/src/features/invoices/components/InvoiceListPlaceholder.test.tsx` | Frontend component/unit | N/A (runner created in PR4) | ✅ Tests added before dependency install; first `npm test` failed with `vitest: command not found` | ✅ `npm test` passed: 4/4 after Vitest/RTL setup | ✅ Covered rendered accessible regions plus bounded-context query keys for both modules | ➖ None needed |
| 3.7 | `.github/workflows/ci.yml`, `uv.lock`, `frontend/package-lock.json` | CI/tooling | N/A (new workflow) | ✅ Verify warning identified missing lockfiles; `uv sync --locked --dev`/`npm ci` were not enforceable before lockfiles existed | ✅ Generated `uv.lock` and `frontend/package-lock.json`; CI now uses `uv sync --locked --dev`, `npm ci`, and frontend cache dependency path | ✅ Reproducible install checks passed locally for backend and frontend lockfiles | ✅ Kept tooling changes within PR4 scope |

## Test Summary

- Backend tests: `uv run pytest` → 5 passed.
- Frontend tests: `npm test` → 4 passed.
- Backend lint/type: `uv run ruff check backend/src backend/tests` → passed; `uv run pyright` → passed.
- Frontend lint/type: `npm run lint` → passed; `npm run typecheck` → passed.
- Approval tests: None — no refactoring tasks.
- Pure functions created: 0; PR4 is tooling/scaffold wiring only.

## PR4 Verify Warning Fixes

| Warning | Resolution | Evidence |
|---------|------------|----------|
| Missing dependency lockfiles | Added `uv.lock` and `frontend/package-lock.json`; updated CI to use locked installs. | `uv sync --locked --dev` passed; `npm ci` passed; lockfile sizes are 523 lines and 3,938 lines respectively. |
| Flyway SQL not executed by Flyway runner | Added a `flyway` Docker Compose service and CI migration-validation job that applies `migrations/sql/V1__base_schema.sql` against the PostgreSQL service. | `docker compose config` passed with PostgreSQL and Flyway services. Local execution command is `docker compose up -d postgres && docker compose run --rm flyway`; it could not run locally because the Docker daemon is unavailable. |
| Route registration test implementation-detail coupled | Replaced `app.state.registered_router_prefixes` assertion with HTTP behavior assertions through FastAPI `TestClient`; added scaffold GET handlers returning explicit `501` responses for CRM customers and Sales invoices. | RED: `404 != 501`; GREEN: `uv run pytest backend/tests/test_app_scaffold.py` passed 3/3; full `uv run pytest` passed 5/5. |

## Warning-Fix Verification Commands

- `uv sync --locked --dev` → passed.
- `uv run pytest` → 5 passed.
- `uv run ruff check backend/src backend/tests` → passed.
- `uv run pyright` → 0 errors, 0 warnings.
- `npm ci` → passed.
- `npm run lint` → passed.
- `npm run typecheck` → passed.
- `npm test` → 2 files / 4 tests passed.
- `docker compose config` → passed.
- `docker compose up -d postgres && docker compose run --rm flyway` → blocked locally by unavailable Docker daemon; CI has the runnable Flyway validation path.

## Phase 4 Completion

### Files Changed in Phase 4

- `openspec/changes/defer-detailed-module-specs/proposal.md` — follow-up OpenSpec proposal for deferred module specs.
- `openspec/changes/defer-detailed-module-specs/design.md` — spec-authoring boundaries and planned spec paths.
- `openspec/changes/defer-detailed-module-specs/tasks.md` — review-budget-aware task plan for the deferred detailed specs.
- `openspec/changes/Read AGENTS.md and all files under docs/. Act as a Principal Software Architect. Review the project structure and suggest improvements./tasks.md` — marked tasks 4.1 and 4.2 complete.
- `openspec/changes/Read AGENTS.md and all files under docs/. Act as a Principal Software Architect. Review the project structure and suggest improvements./apply-progress.md` — merged prior progress and recorded Phase 4 completion.

### TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 4.1 | N/A | Planning/docs | N/A — OpenSpec planning artifact only | N/A — no executable behavior added | N/A — artifacts created and re-read | N/A — no runtime behavior | N/A |
| 4.2 | N/A | Planning/docs | N/A — scope boundary documentation only | N/A — no executable behavior added | N/A — no business logic or detailed specs added | N/A — no runtime behavior | N/A |

### Verification

- Re-read the updated foundation `tasks.md` and confirmed 4.1 and 4.2 are checked.
- Re-read the new follow-up `proposal.md`, `design.md`, and `tasks.md` to confirm the change plans deferred detailed specs without implementing business logic.
