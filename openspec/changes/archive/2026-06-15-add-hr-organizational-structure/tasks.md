# Tasks: Add HR Organizational Structure

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650-900 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 contracts/scaffold/docs → PR 2 domain/service rules |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Import-safe HR/Accounting/UoW contracts, HR 501 routes, docs, scaffold tests | PR 1 | Base branch TBD; no persistence. |
| 2 | HR domain/service invariants with test-first fakes | PR 2 | Depends on PR 1; no workflow runtime. |

## Phase 1: Contract and Scaffold RED Tests

- [x] 1.1 Add failing route assertions to `backend/tests/test_app_scaffold.py` for `GET /hr/organizational-units` and `GET /hr/positions` returning 501.
- [x] 1.2 Add failing UoW assertions to `backend/tests/test_uow_contract.py` for `hr_organization` and `accounting_cost_centers` protocol attributes.
- [x] 1.3 Create failing domain tests in `backend/tests/hr/test_organization_domain.py` for vacant position validity, effective superior lookup, one active assignment, and Decimal allocation total 100%.
- [x] 1.4 Create failing service tests in `backend/tests/hr/test_organization_service.py` for inactive Accounting cost-center rejection, no approval workflow side effects, planned organization use-case contract exposure, and repository-backed concurrent active assignment rejection.

## Phase 2: Contract and Scaffold GREEN

- [x] 2.1 Create `backend/src/hr/__init__.py` and `backend/src/hr/controllers/routes.py` with `/hr/organizational-units` and `/hr/positions` route constants plus 501 scaffold endpoints.
- [x] 2.2 Update `backend/src/main.py` to include the HR router after CRM/Sales routers.
- [x] 2.3 Create `backend/src/accounting/repositories/contracts.py` with `AccountingCostCenterLookupPort` and validation result types.
- [x] 2.4 Create `backend/src/hr/repositories/contracts.py` with `HROrganizationRepository` protocol for tenant-scoped units, positions, hierarchy, assignments, and allocations.
- [x] 2.5 Modify `backend/src/shared/uow/ports.py` to expose HR organization and Accounting cost-center lookup ports.

## Phase 3: Domain and Service GREEN

- [x] 3.1 Create `backend/src/hr/domain/organization.py` dataclasses/enums with tenant IDs, effective dates, audit fields, vacancy state, vinculation references, and Decimal allocations.
- [x] 3.2 Implement domain helpers in `backend/src/hr/domain/organization.py` for superior lookup, overlapping assignment detection, and exact 100% allocation validation.
- [x] 3.3 Create `backend/src/hr/schemas/organization.py` explicit request/response/query dataclasses exposing cost-center codes in allocation read models.
- [x] 3.4 Create `backend/src/hr/services/organization.py` `OrganizationService` protocol/contract for create/list units, create positions, set superior, assign employee, validate authorization target, and set allocations.

## Phase 4: Documentation and Verification

- [x] 4.1 Update `docs/bounded-context.md` so HR owns units/positions/assignments/allocations and Accounting owns cost-center catalog lifecycle.
- [x] 4.2 Keep `backend/migrations/*.sql` out of this slice; document Flyway SQL tables as later work until migration scaffolding exists.
- [x] 4.3 Run `uv run pytest backend/tests/test_app_scaffold.py backend/tests/test_uow_contract.py backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py`; if tooling scaffolding is missing, record the blocker and preserve RED tests.
- [x] 4.4 Refactor only for import safety, explicit contracts, and no direct cross-context table access.
