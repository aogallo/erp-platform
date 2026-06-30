# Tasks: Cover HR Organization Audit Tests

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 60-110 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR: #31 focused pytest coverage only |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Add bounded UTC audit timestamp tests for existing HR organization creation paths | PR 1 | Single focused test-only PR for #31; no #32 runtime work |

## Phase 1: Test Foundation

- [x] 1.1 Update `backend/tests/hr/test_organization_service.py` imports to include `UTC` and `datetime` for timezone-aware bounded assertions.
- [x] 1.2 Add a test-local helper in `backend/tests/hr/test_organization_service.py` that asserts `created_by`, `tzinfo is UTC`, and `before <= created_at <= after`.

## Phase 2: RED — Audit Coverage Tests

- [x] 2.1 Add pytest-asyncio coverage for `create_organizational_unit` proving actor and bounded UTC `created_at` from `CreateOrganizationalUnitCommand.actor_id`.
- [x] 2.2 Add pytest-asyncio coverage for `create_position`, seeding an organizational unit and asserting actor plus bounded UTC `created_at`.
- [x] 2.3 Add pytest-asyncio coverage for `set_superior_position`, seeding current and superior positions and asserting actor plus bounded UTC `created_at`.
- [x] 2.4 Add pytest-asyncio coverage for `assign_position`, seeding a position and asserting actor plus bounded UTC `created_at` on the stored assignment.

## Phase 3: GREEN / Scope Guard

- [x] 3.1 Run `uv run pytest backend/tests/hr/test_organization_service.py` and keep production code unchanged unless an existing creation path fails #31 timestamp expectations.
- [x] 3.2 Confirm no runtime tasks or code changes were added for #32 update APIs, update commands, repositories, audit-state persistence, or cost allocation audit stamping.

## Phase 4: Verification

- [x] 4.1 Run `uv run pytest` if project dependencies are available; otherwise record the environment blocker in verification.
- [x] 4.2 Update this task list during apply by marking completed items only after tests and scope guard checks pass.
