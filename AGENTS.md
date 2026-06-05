# ERP Assistant Context

You are helping build an ERP system.

## Architecture

- FastAPI
- PostgreSQL
- Flyway
- SQLAlchemy
- Canonical architecture: Hexagonal Architecture + DDD by bounded-context feature folders.

## Rules

- Use DDD concepts.
- Use Repository Pattern.
- Use Service Layer.
- Follow Hexagonal Architecture.
- Database is source of truth.
- Do no generate automatic migrations.
- Prefer SQL migrations.
- Use route prefixes by bounded context, for example `/crm/customers` and `/sales/invoices`.
- Treat `docs/bounded-context.md` as the canonical context map.

## Bounded Contexts

- IAM
- CRM
- Sales
- Inventory
- Purchasing
- Accounting
- Banking
- HR
