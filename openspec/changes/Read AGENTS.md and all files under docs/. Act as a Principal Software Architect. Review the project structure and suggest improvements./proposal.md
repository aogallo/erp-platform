# Proposal: Architecture Foundation & Spec Definition

## Intent

Resolve contradictions in architecture docs, reconcile bounded contexts, define cross-cutting concerns, write critical module specs, and set up project infrastructure — all before any business logic is coded.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Fix architecture contradiction (drop Vertical Slice) | Business logic implementation |
| Canonicalize 8 bounded contexts with context map | Remaining module specs (Inventory, Accounting, Purchasing, HR, Sales, Banking) — deferred |
| Write cross-cutting concern docs (Unit of Work, error handling, logging, auth, FEL, multi-tenancy) | |
| Write Customer + Invoice module specs | |
| Backend/frontend project scaffolding, Docker Compose, CI, pytest/Vitest, Flyway base | |

## Capabilities

### New Capabilities
- `customer`: Customer registration, updates, contacts, communication tracking
- `invoice`: Invoice creation, posting, immutability after posting, asynchronous FEL authorization, credit notes, automatic accounting entry generation

### Modified Capabilities
None — all existing spec files under `docs/modules/` are empty placeholders, not canonical `openspec/specs/` files.

## Approach

**P1 — Architecture Foundation**: Edit `coding-standards.md` (drop Vertical Slice, keep Hexagonal + DDD). Rewrite `bounded-context.md` (8 contexts: IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, HR + relationships). Write ADR-001. Update `AGENTS.md`. Write cross-cutting concern docs/ADRs.

Backend feature folders (`src/{bounded-context}/`):
- `controllers/` — FastAPI routers + request/response schemas
- `services/` — Business logic, orchestration
- `repositories/` — SQLAlchemy data access
- `domain/` — Entities, value objects, domain events
- `schemas/` — Pydantic models

Frontend (`frontend/`): React + TypeScript + Vite. Feature-based:
- `components/`, `hooks/`, `types/`, `api/` (TanStack Query functions per feature)

Shared kernel: auth middleware, Unit of Work, Transactional Outbox, error handling, structured logging.

**Auth**: Self-hosted. Evaluate fastapi-fullauth (most mature FastAPI-native, SQLAlchemy adapter, RBAC, OAuth2, passkeys, rate limiting) vs AuthFort (TypeScript client SDK, JWKS, multi-DB). Design as **swappable provider** — domain defines auth interface (login, register, verify, RBAC), infrastructure plugs in the chosen lib. Future: add Auth0/OIDC provider adapter without touching domain.

**FEL**: Infile (certified provider, de facto standard in Guatemala). Adapter/port + asynchronous authorization:
- Domain: `FELInvoiceService` interface (send, cancel, query, retry)
- Infrastructure: `InfileAdapter` via digifact-sdk or Infile SOAP/API
- Process: local invoice posting commits inventory + accounting + outbox event; worker requests FEL; failures retry without rolling back the sale
- Benefits: provider outages do not block internal posting; provider can be swapped without touching domain logic

**P2 — Critical Module Specs**: Write `openspec/specs/customer/spec.md` and `openspec/specs/invoice/spec.md` with Given/When/Then scenarios, domain invariants, and business rules.

**P3 — Scaffolding**: Create project structure, Docker Compose (PostgreSQL), `pytest` + `pytest-asyncio`, Vitest, GitHub Actions CI (ruff, mypy/pyright, tests, coverage), Flyway base migration.

**P4 — Future**: Remaining module specs deferred to a follow-up change.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `docs/coding-standards.md` | Modified | Drop Vertical Slice |
| `docs/bounded-context.md` | Rewritten | 8 contexts + context map |
| `docs/architecture.md` | Modified | Align with canonical context list |
| `AGENTS.md` | Modified | Update bounded context list |
| `openspec/specs/customer/spec.md` | New | Customer module spec |
| `openspec/specs/invoice/spec.md` | New | Invoice module spec |
| `src/`, `frontend/` | New | Project structure |
| `docker-compose.yml` | New | Local PostgreSQL |
| `.github/workflows/ci.yml` | New | CI pipeline |
| `migrations/` | New | Flyway base |
| `openspec/config.yaml` | Modified | Fill in testing tool config |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Architecture debate stalls progress | Med | ADR-001 with clear rationale |
| Auth library doesn't fit requirements | Low | Interface + adapter — swappable; Auth0 path documented |
| FEL provider lock-in | Low | Adapter pattern — Infile first, provider-agnostic domain interface |
| Self-hosted auth operational burden | Med | fastapi-fullauth is pip-installable, minimal ops; document migration path to Auth0 |

## Rollback Plan

Git revert on modified doc files (`docs/*`, `AGENTS.md`). New scaffolding files are additive — revert by deleting the branch.

## Dependencies

- fastapi-fullauth or AuthFort (evaluate in P1, self-hosted, swappable to Auth0)
- Infile account + digifact-sdk (FEL adapter skeleton, evaluate in P1)
- Docker Compose (local PostgreSQL for dev)

## Success Criteria

- [ ] `coding-standards.md` no longer mentions Vertical Slice
- [ ] `bounded-context.md` defines all 8 contexts with relationships
- [ ] ADR-001 written for Hexagonal + DDD decision
- [ ] `openspec/specs/customer/spec.md` exists with business rules and scenarios
- [ ] `openspec/specs/invoice/spec.md` exists with invoice lifecycle, asynchronous FEL rules, posting invariants
- [ ] `pytest tests/` passes (no-op test)
- [ ] `docker-compose up -d` starts PostgreSQL
