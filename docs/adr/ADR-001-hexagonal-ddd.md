# ADR-001: Hexagonal Architecture with DDD Feature Folders

## Status

Accepted

## Context

The ERP is greenfield, but existing guidance mixed Clean Architecture, Vertical Slice, and DDD. The system needs clear ownership across IAM, CRM, Sales, Inventory, Purchasing, Accounting, Banking, and HR while keeping domain rules independent from FastAPI, SQLAlchemy, and external providers.

## Decision

Use Hexagonal Architecture with Domain-Driven Design, organized by bounded-context feature folders.

Each backend context uses:

```text
backend/src/{context}/controllers|services|repositories|domain|schemas
```

Controllers are inbound adapters, repositories are outbound adapters, services coordinate use cases, and domain objects hold business rules. Cross-cutting concerns live behind ports/adapters and are documented under `docs/cross-cutting/`.

## Alternatives Considered

- Vertical Slice Architecture: rejected because it can duplicate transaction, provider, and domain rules across slices in a modular ERP.
- Layer-first Clean Architecture: rejected because global layers hide bounded-context ownership and make ERP module discovery harder.
- Provider-first implementation: rejected because auth and FEL providers must remain swappable.

## Consequences

- Domain code remains framework-independent.
- API routes expose context ownership through prefixes such as `/crm/customers` and `/sales/invoices`.
- Cross-context workflows require application services and transaction-manager boundaries.
- More upfront structure is required, but it protects long-term modularity.

## Rollback

Revert this ADR and related documentation changes. If code has already followed this decision, rollback requires moving context folders or introducing compatibility adapters before changing public routes.
