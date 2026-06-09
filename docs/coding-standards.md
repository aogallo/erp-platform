---
name: Coding Standards
description: Defines development conventions, architectural rules, coding practices, naming conventions, and quality requirements.
---

# Backend

Language: Python 3.13

Framework: FastAPI

## Architecture

- Hexagonal Architecture
- Domain-Driven Design
- Feature folders by bounded context

Backend code MUST be organized by canonical bounded context, not by technical layer alone:

```text
backend/src/{context}/
  controllers/    # FastAPI inbound adapters and HTTP schemas
  services/       # Application services and orchestration
  repositories/   # SQLAlchemy outbound adapters
  domain/         # Entities, value objects, domain events, domain services
  schemas/        # Pydantic models shared by adapters/application layer
```

The domain layer MUST NOT import FastAPI, SQLAlchemy sessions, Pydantic request models, or provider SDKs. Controllers call services; services coordinate repositories through a Unit of Work; repositories own database access.

## Backend Model Boundaries

Keep these three model types separate:

```text
Domain entity ≠ SQLAlchemy ORM model ≠ Pydantic schema
```

| Type | Purpose | Location | Depends on |
|------|---------|----------|------------|
| Domain entity | Business rules and domain state | `backend/src/{context}/domain/` | Pure Python only |
| SQLAlchemy ORM model | Table mapping and persistence concerns | `backend/src/{context}/repositories/models.py` | SQLAlchemy |
| Pydantic schema | HTTP request/response validation | `backend/src/{context}/schemas/` | Pydantic |

Flow:

```text
Controller
  receives Pydantic schemas
    ↓
Service
  works with domain entities and value objects
    ↓
Repository
  maps domain entities ↔ SQLAlchemy ORM models
    ↓
Database
```

Repositories MAY define SQLAlchemy 2.x declarative models in `models.py` and persistence adapters in `sqlalchemy.py`. Controllers MUST return Pydantic response schemas, never SQLAlchemy ORM models.

## Patterns

- Repository Pattern
- Service Pattern
- Unit of Work Pattern
- Dependency Injection

## Shared Types

- Paginated application results MUST use `backend/src/shared/pagination.py::Page[T]`.
- Bounded contexts MUST NOT define their own `Page` or pagination response clones.
- Context services SHOULD type paginated results explicitly, for example `Page[InvoiceRead]`.
- HTTP response schemas MAY add transport-specific aliases such as `pageSize`, but those aliases belong at the HTTP boundary, not in context-local pagination types.

## Requirements

- `uv` is the backend environment and dependency manager.
- `pyproject.toml` and `uv.lock` MUST be committed.
- Backend commands MUST run through `uv run` in local development and CI.
- Backend runtime configuration MUST use `pydantic-settings` with typed settings, `ERP_` environment variable prefix, and local `.env` fallback for development.
- `.env` MUST NOT be committed; `.env.example` MUST document safe development defaults.
- Ruff is the formatter, linter, and import sorter.
- Pyright is the default Python type checker; mypy MAY be added later if needed.
- Type hints required
- Pydantic v2 required
- SQLAlchemy 2.x required
- Async endpoints preferred
- Unit tests required
- Integration tests required
- Request and response schemas SHOULD be explicit; SQLAlchemy models MUST NOT be returned directly from API routes.
- Monetary values MUST use `Decimal`, never `float`.
- Timestamps MUST use UTC.
- Application configuration MUST use the shared typed settings module, not scattered environment reads.

## Forbidden

- Business logic in controllers
- Direct database access from controllers
- Circular dependencies
- Cross-context writes without an application service and Unit of Work boundary
- Provider SDK calls from domain objects
- `session.commit()` outside Unit of Work boundaries
- `requirements.txt` as the dependency source of truth
- Returning ORM models directly from controllers

## Naming

- snake_case for variables
- PascalCase for classes
- UPPER_CASE for constants

# Frontend

Language: TypeScript

## Framework

- React
- Vite

## Architecture

- Feature-based structure aligned to backend bounded contexts

Frontend features SHOULD mirror business capabilities and consume bounded-context routes such as `/crm/customers` and `/sales/invoices`. Server state belongs in TanStack Query hooks under the feature `api/` folder.

## Requirements

- Functional components only
- TypeScript strict mode
- TanStack Query for server state
- Zod for validation
- Feature folders SHOULD use this structure:

```text
frontend/src/features/{feature}/
  api/          # TanStack Query functions, query keys, mutations
  components/   # Feature UI components
  hooks/        # Feature-specific hooks
  schemas/      # Zod schemas
  types/        # TypeScript types
```

- Query keys MUST be centralized per feature.
- Server state belongs in TanStack Query; local UI state belongs in React state.
- Forms SHOULD validate through Zod schemas.
- Components SHOULD expose accessible labels, semantic buttons, loading states, and error states.
- Large components SHOULD be split into container and presentational components when behavior and rendering become hard to read.

## Forbidden

- Class components
- Any type without justification
- Direct `fetch` or API client calls from React components
- Duplicated query keys across files
- Business workflow logic embedded in presentational components

## Naming

- camelCase for variables
- PascalCase for components
- kebab-case for folders
- `import type` SHOULD be used for type-only imports
