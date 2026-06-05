# ERP Assistant Context

You are helping build a modular ERP system. Optimize for maintainability, explicit business rules, and implementation that another developer or AI agent can continue without guessing.

## Canonical References

Read these before designing or implementing features:

- `docs/bounded-context.md` — canonical bounded context map.
- `docs/coding-standards.md` — Python/FastAPI and React/TypeScript conventions.
- `docs/cross-cutting/*.md` — shared contracts for Unit of Work, auth, FEL, logging, errors, and multi-tenancy.
- `openspec/specs/` — canonical behavior specs.

## Stack

| Area | Standard |
|------|----------|
| Backend | FastAPI, Python 3.13, SQLAlchemy 2.x, Pydantic v2 |
| Database | PostgreSQL; SQL migrations with Flyway |
| Frontend | React, TypeScript, Vite, TanStack Query, Zod |
| Tooling | `uv`, Ruff, Pyright, pytest, Vitest |

## Architecture Rules

- Use Hexagonal Architecture + DDD by bounded-context feature folders.
- Use Repository Pattern for persistence access.
- Use Service Layer for application orchestration and business workflows.
- Use Unit of Work for transactions; do not call `session.commit()` directly from controllers/services outside the UoW boundary.
- Database is the source of truth.
- Do not generate automatic migrations. Write reviewable SQL migrations.
- Keep provider SDKs in infrastructure adapters only, never in domain objects.
- Use route prefixes by bounded context, for example `/crm/customers`, `/sales/invoices`, `/banking/checks`.

## Backend Structure

```text
src/{context}/
  controllers/    # FastAPI routers and HTTP schemas
  services/       # Application services and orchestration
  repositories/   # SQLAlchemy data access adapters
  domain/         # Entities, value objects, domain events, domain services
  schemas/        # Pydantic request/response models

src/shared/
  auth/
  config/
  errors/
  fel/
  logging/
  outbox/
  uow/
```

## Frontend Structure

```text
frontend/src/features/{feature}/
  api/          # TanStack Query functions, query keys, mutations
  components/
  hooks/
  schemas/      # Zod schemas
  types/
```

## Bounded Contexts

- IAM — authentication, RBAC, users, roles, permissions, tenant scope.
- CRM — customers, contacts, customer master data.
- Sales — quotes, orders, invoices, invoice posting, credit notes.
- Inventory — products, stock, stock movements, valuation inputs.
- Purchasing — suppliers, purchase orders, goods receipts, payables inputs.
- Accounting — chart of accounts, journal entries, financial reports.
- Banking — bank accounts, checks, deposits, debit/credit notes, bank movements, reconciliation.
- HR — employees, contracts, payroll inputs, bonuses, legal deductions, suspensions.

## Cross-Cutting Decisions

- Auth is self-hosted by default with `fastapi-fullauth` as the first candidate.
- Authorization uses RBAC: users get roles, roles get permissions, contexts check permissions.
- FEL uses Infile first, behind a swappable adapter.
- FEL authorization is asynchronous through Transactional Outbox; provider outages must not roll back local invoice posting after commit.
- Money must use `Decimal`, never `float`.
- Timestamps must use UTC.
- Request/response schemas must be explicit; do not return ORM models directly.

## Testing Policy

- Strict TDD is the project policy.
- Backend tests use pytest/pytest-asyncio.
- Frontend tests use Vitest.
- Until scaffolding exists, document intended tests in specs/design/tasks; once tooling exists, write tests before implementation.

## Do Not

- Do not place business logic in controllers.
- Do not access the database directly from controllers.
- Do not couple one bounded context to another context's tables directly.
- Do not hard-code roles in business logic; check permissions.
- Do not call Infile/FEL synchronously inside the local invoice posting transaction.
- Do not use `requirements.txt` as the backend dependency source of truth.
