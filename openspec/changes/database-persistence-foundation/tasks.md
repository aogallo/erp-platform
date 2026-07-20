# Tasks: Database Persistence Foundation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 450-650 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 migrations/config → PR 2 SQLAlchemy foundation → PR 3 UoW behavior/static guard |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Flyway baseline and database settings | PR 1 | Includes migration/config tests; no business tables. |
| 2 | SQLAlchemy async metadata/session foundation | PR 2 | Depends on PR 1 settings; includes metadata/session tests. |
| 3 | Concrete SQLAlchemy UoW boundary | PR 3 | Depends on PR 2; includes commit/rollback and raw-commit guard tests. |

## Phase 1: Flyway Baseline and Settings

- [x] 1.1 RED: Add migration tests under `backend/tests/` asserting `backend/migrations/sql/V1__database_foundation.sql` enables `pgcrypto`, creates only the eight context schemas, and creates no business tables.
- [x] 1.2 GREEN: Create `backend/flyway.conf` and `backend/migrations/sql/V1__database_foundation.sql` with `CREATE EXTENSION IF NOT EXISTS pgcrypto` and schemas `iam`, `crm`, `sales`, `inventory`, `purchasing`, `accounting`, `banking`, `hr`.
- [x] 1.3 RED: Extend settings tests for async SQLAlchemy URL behavior and Flyway-friendly connection names in `backend/src/shared/config/settings.py`.
- [x] 1.4 GREEN: Update `backend/src/shared/config/settings.py` without removing current environment-backed defaults.
- [x] 1.5 REVIEW CORRECTION: Update `backend/flyway.conf` to reference explicit `ERP_DATABASE_*` environment variables and add a static contract test for the Flyway configuration.

## Phase 2: SQLAlchemy Foundation

- [x] 2.1 RED: Add tests for `backend/src/shared/db/sqlalchemy.py` metadata naming conventions, declarative `Base`, async engine creation, and `async_sessionmaker` wiring.
- [x] 2.2 GREEN: Add SQLAlchemy to `pyproject.toml` and create `backend/src/shared/db/__init__.py`, `backend/src/shared/db/settings.py` if needed, and `backend/src/shared/db/sqlalchemy.py`.
- [x] 2.3 REFACTOR: Keep migrations as source of truth; document future context model location in module docstrings only if needed.

## Phase 3: Unit of Work Transaction Boundary

- [ ] 3.1 RED: Add async tests proving `SqlAlchemyUnitOfWork` commits once on `commit()` and rolls back uncommitted work on exception.
- [ ] 3.2 RED: Add a focused static test that repository files under `backend/src/**/repositories/` do not call `session.commit()`.
- [ ] 3.3 GREEN: Create `backend/src/shared/uow/contracts.py` re-exporting existing `UnitOfWork` protocols from `ports.py` for compatibility; do not add new `ports.py` files.
- [ ] 3.4 GREEN: Create `backend/src/shared/uow/sqlalchemy.py` with concrete async UoW using `async_sessionmaker[AsyncSession]`; update `backend/src/shared/uow/__init__.py` exports.
- [ ] 3.5 REFACTOR: Ensure controllers/services/repositories retain UoW-owned commit/rollback and no raw commits outside the UoW boundary.

## Phase 4: Verification

- [ ] 4.1 Run `uv run pytest` and fix failures in the same work unit that introduced them.
- [ ] 4.2 Confirm no business tables, seed data, schema-per-tenant isolation, or enabled RLS policies were added.
