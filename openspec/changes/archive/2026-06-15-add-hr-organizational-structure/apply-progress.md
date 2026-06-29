# Apply Progress: Add HR Organizational Structure

**Change**: `add-hr-organizational-structure`
**Mode**: Strict TDD
**Artifact store**: OpenSpec
**Last updated**: 2026-06-15

## Cumulative Task Status

All tasks in `tasks.md` are complete as of the merged PR slices:

- PR #28: scaffold, contracts, OpenSpec artifacts, and bounded-context documentation.
- PR #30: HR domain model, service contract/application service, schemas, and runtime tests.

This fix batch addresses the verification gaps reported in `verify-report.md` without changing the completed task checklist.

## TDD Cycle Evidence

| Task / Gap | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1 HR route scaffold assertions | `backend/tests/test_app_scaffold.py` | HTTP scaffold | PR #28 evidence; current verifier saw targeted suite pass | Tests were introduced before route scaffold in PR #28 per task sequence | 501 HR route scaffold passed in verifier run: 15/15 targeted tests | Two route cases: `/hr/organizational-units`, `/hr/positions` | Import-safe route constants and router registration kept clean |
| 1.2 UoW HR/Accounting ports | `backend/tests/test_uow_contract.py` | Contract/static | PR #28 evidence; current verifier saw targeted suite pass | UoW assertions were introduced before port attributes in PR #28 per task sequence | UoW contract tests passed in verifier run: 15/15 targeted tests | Two added attributes: `hr_organization`, `accounting_cost_centers` | Repository modules use `contracts.py`; no `ports.py` drift |
| 1.3 HR domain invariants | `backend/tests/hr/test_organization_domain.py` | Unit | PR #30 evidence; current verifier saw targeted suite pass | Domain tests were introduced before dataclasses/helpers in PR #30 per task sequence | Domain tests passed in verifier run: 15/15 targeted tests | Vacancy, superior lookup, overlap rejection, exact Decimal 100 allocation | Domain remains pure dataclasses/helpers |
| 1.4 / 3.4 HR service behavior | `backend/tests/hr/test_organization_service.py` | Unit with fakes | PR #30 evidence; current verifier saw targeted suite pass | Service tests were introduced before application-service behavior in PR #30 per task sequence | Service tests passed in verifier run: 15/15 targeted tests | Inactive cost center, vacancy escalation, planned use cases, concurrent assignment | No approval workflow side effects; UoW boundary preserved |
| Fix: cross-tenant organizational unit rejection | `backend/tests/hr/test_organization_service.py::test_create_position_rejects_cross_tenant_organizational_unit` | Unit with fakes | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | Test added before production changes; existing service behavior already rejected tenant B lookup | `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed after fix batch GREEN | Tenant A unit cannot be used from tenant B; repository positions stay empty and commit count remains 0 | No production refactor needed |
| Fix: professional-services label not decisive | `backend/tests/hr/test_organization_service.py::test_professional_services_label_is_not_decisive_for_vinculation` | Unit with fakes | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | RED confirmed: `TypeError: AssignPositionCommand.__init__() got an unexpected keyword argument 'vinculation_type'` | Added explicit `vinculation_type` command field and service mapping; `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed | Label-only reference remains unclassified; explicit configured type is stored only when provided | Formatting cleanup after Ruff E501 findings; service tests still 9 passed |
| Fix: IAM linkage ownership remains HR-owned | `backend/tests/hr/test_organization_service.py::test_iam_linkage_remains_employee_reference_owned_by_hr_assignment` | Unit with fakes | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | Test added before production changes; existing assignment model already exposed HR employee reference and no IAM ownership field | `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed | Asserts employee reference, actor audit, no `iam_user_id`, and repository-owned assignment | No production refactor needed |
| Fix: Accounting cost-center lifecycle ownership/read contract | `backend/tests/hr/test_organization_service.py::test_accounting_cost_center_contract_is_lookup_only_for_hr` | Contract/static | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | Test added before production changes; existing contracts already exposed lookup-only boundary | `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed | Verifies lookup method exists and lifecycle methods are absent from Accounting lookup, HR repository, and HR service contracts | No production refactor needed |
| Fix: HR cannot create/activate/deactivate Accounting cost centers | `backend/tests/hr/test_organization_service.py::test_accounting_cost_center_contract_is_lookup_only_for_hr` | Contract/static | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | Test added before production changes; existing contracts already prevented HR lifecycle methods | `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed | Same lifecycle-method absence assertions cover create, activate, and deactivate attempts at the HR contract boundary | No production refactor needed |
| Fix: active cost-center success allocation | `backend/tests/hr/test_organization_service.py::test_set_position_cost_allocation_persists_split_and_returns_codes` | Unit with fakes | `uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py` → 8 passed before edits | Test added before production changes; existing service behavior passed after fake captured tenant/effective-date calls and persisted allocations | `uv run pytest backend/tests/hr/test_organization_service.py` → 9 passed | Validates Accounting calls, 60/40 persisted allocations, returned cost-center codes, exact 100 total, one commit | Test fake refactored to store allocation records and call tuples; Ruff E501 cleanup completed |

## Current Fix Batch Command Evidence

### Safety Net

```text
Command: uv run pytest backend/tests/hr/test_organization_domain.py backend/tests/hr/test_organization_service.py
Result: PASS

8 passed in 0.02s
```

### RED

```text
Command: uv run pytest backend/tests/hr/test_organization_service.py
Result: FAIL

FAILED backend/tests/hr/test_organization_service.py::test_professional_services_label_is_not_decisive_for_vinculation
TypeError: AssignPositionCommand.__init__() got an unexpected keyword argument 'vinculation_type'
```

Other new tests were written before production changes and passed against already-implemented behavior, converting previously untested spec scenarios into direct runtime evidence.

### GREEN

```text
Command: uv run pytest backend/tests/hr/test_organization_service.py
Result: PASS

9 passed in 0.02s
```

### REFACTOR

```text
Command: uv run ruff check backend/src/hr/schemas/organization.py backend/src/hr/services/organization.py backend/tests/hr/test_organization_service.py
Result: FAIL

3 E501 line-length findings in the new test file.

Command: uv run pytest backend/tests/hr/test_organization_service.py
Result: PASS

9 passed in 0.02s

Command: uv run ruff check backend/src/hr/schemas/organization.py backend/src/hr/services/organization.py backend/tests/hr/test_organization_service.py
Result: PASS

All checks passed!
```

## Spec Gap Coverage Added in This Batch

| Verification gap | Direct runtime evidence |
|---|---|
| Cross-tenant organizational unit rejection | `test_create_position_rejects_cross_tenant_organizational_unit` |
| Professional-services label not decisive | `test_professional_services_label_is_not_decisive_for_vinculation` |
| IAM linkage ownership remains HR-owned | `test_iam_linkage_remains_employee_reference_owned_by_hr_assignment` |
| Accounting cost-center catalog lifecycle ownership/read contract | `test_accounting_cost_center_contract_is_lookup_only_for_hr` |
| HR cannot create/activate/deactivate Accounting cost centers | `test_accounting_cost_center_contract_is_lookup_only_for_hr` |
| Active cost-center success allocation with 60/40 persistence and returned codes | `test_set_position_cost_allocation_persists_split_and_returns_codes` |

## Production Changes in This Batch

- `backend/src/hr/schemas/organization.py`: added optional explicit `vinculation_type` to `AssignPositionCommand`.
- `backend/src/hr/services/organization.py`: maps explicit `vinculation_type` into `PositionAssignment` without inferring it from a label/reference string.

## Design Alignment Notes

- Terminology remains `Position`, not `Plaza`.
- HR and Accounting repository modules continue to use `contracts.py`.
- `PositionCostAllocation` still stores one or more Accounting cost-center references and enforces exact `Decimal("100")` total.
- Accounting owns cost-center lifecycle; HR validates/references active cost centers only.
