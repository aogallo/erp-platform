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
src/{context}/
  controllers/    # FastAPI inbound adapters and HTTP schemas
  services/       # Application services and orchestration
  repositories/   # SQLAlchemy outbound adapters
  domain/         # Entities, value objects, domain events, domain services
  schemas/        # Pydantic models shared by adapters/application layer
```

The domain layer MUST NOT import FastAPI, SQLAlchemy sessions, Pydantic request models, or provider SDKs. Controllers call services; services coordinate repositories through a Unit of Work; repositories own database access.

## Patterns

- Repository Pattern
- Service Pattern
- Unit of Work Pattern
- Dependency Injection

## Requirements

- Type hints required
- Pydantic v2 required
- SQLAlchemy 2.x required
- Async endpoints preferred
- Unit tests required
- Integration tests required

## Forbidden

- Business logic in controllers
- Direct database access from controllers
- Circular dependencies
- Cross-context writes without an application service and Unit of Work boundary
- Provider SDK calls from domain objects

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
- React Query for server state
- Zod for validation

## Forbidden

- Class components
- Any type without justification

## Naming

- camelCase for variables
- PascalCase for components
- kebab-case for folders
