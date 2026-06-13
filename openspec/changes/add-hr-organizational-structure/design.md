# Design: Add HR Organizational Structure

## Technical Approach

Add HR organizational master data as a new HR backend slice that follows the current scaffold pattern: pure dataclass domain objects, service/repository `Protocol` contracts, explicit schema shapes, FastAPI route scaffolds, and Unit of Work ports. HR owns organizational units, plazas, reporting lines, assignments, and allocation records. Accounting owns cost centers and exposes only a validation/read boundary for HR allocation references. No approval workflow runtime is implemented; the HR contract only exposes vacancy and superior-plaza data needed by future approval consumers.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| HR owns plazas | Model `OrganizationalUnit`, `Plaza`, `PlazaReportingLine`, `PlazaAssignment`, and `PlazaCostAllocation` under `backend/src/hr/domain/`. | Store positions in IAM roles or Accounting dimensions. | Specs require role-independent HR ownership; IAM stays identity/RBAC-only and Accounting stays finance catalog owner. |
| Effective dating | Store effective date ranges on units, reporting lines, assignments, and allocations. | Overwrite current records in place. | Payroll, hierarchy, and allocation queries need historical answers and UTC auditability. |
| Cost center identity | Store Accounting cost-center database IDs as FK-backed references and expose human-readable codes in contracts/read models. | Use code-only references or duplicate cost-center rows in HR. | The database needs relational integrity, while users and API consumers need readable codes. |
| API shape | Register scaffolded HR routes now, with explicit schema contracts for later implementation. | Wait until persistence is implemented. | Existing CRM/Sales code exposes import-safe route contracts and 501 scaffolds; this keeps the implementation reviewable. |
| Persistence | Plan SQL migrations as reviewable Flyway SQL once migration scaffolding exists. | Auto-generate migrations. | Project rules forbid automatic migrations; the repo currently has no migration directory. |

## Data Flow

```text
HR Controller ──principal/tenant──→ HR Service ──→ UnitOfWork
                                      │              ├─ hr_org_repository
                                      │              └─ accounting_cost_centers.validate_active(...)
                                      └─ domain rules: tenant, dates, percentages, one active assignment
```

For a plaza allocation, the service verifies HR permission and tenant scope, loads the plaza, validates each cost center through Accounting, enforces active references and 100% Decimal percentage total, then stores cost-center database IDs while returning readable codes in read models.

## File Changes

| File | Action | Description |
|---|---|---|
| `backend/src/hr/__init__.py` | Create | HR package marker. |
| `backend/src/hr/domain/organization.py` | Create | Domain dataclasses/enums for units, plazas, hierarchy, single-active assignments, vinculation references, allocations. |
| `backend/src/hr/schemas/organization.py` | Create | Explicit request/response/query dataclasses now; migrate to Pydantic v2 when schema scaffold does. |
| `backend/src/hr/services/organization.py` | Create | `OrganizationService` Protocol for create/list units, create plazas, set superior plaza, assign employee, validate authorization target, and set allocations. |
| `backend/src/hr/repositories/ports.py` | Create | `HROrganizationRepository` Protocol for tenant-scoped org persistence. |
| `backend/src/hr/controllers/routes.py` | Create | `/hr/organizational-units` and `/hr/plazas` route constants plus 501 scaffold endpoint. |
| `backend/src/accounting/repositories/ports.py` | Create | `AccountingCostCenterLookupPort` Protocol returning active/inactive/not-found validation results. |
| `backend/src/shared/uow/ports.py` | Modify | Add HR repository and Accounting cost-center lookup attributes to the Unit of Work contract. |
| `backend/src/main.py` | Modify | Include the HR router. |
| `backend/tests/test_app_scaffold.py` | Modify | Assert HR scaffold route registration. |
| `backend/tests/test_uow_contract.py` | Modify | Assert new UoW attributes are exposed by the protocol. |
| `docs/bounded-context.md` | Modify | Add units, plazas, cost allocation references, and Accounting cost-center boundary to HR/Accounting context map. |
| `backend/migrations/*.sql` | Create later | Tenant-scoped HR org tables and Accounting cost-center table when Flyway scaffold exists. |

## Interfaces / Contracts

```python
class AccountingCostCenterLookupPort(Protocol):
    async def validate_active_cost_center(
        self, *, tenant_id: str, cost_center_id: int, effective_date: date
    ) -> CostCenterValidationResult: ...

class OrganizationService(Protocol):
    async def set_plaza_cost_allocation(
        self, command: PlazaCostAllocationCommand
    ) -> PlazaCostAllocationRead: ...
```

Domain invariants: every record carries `tenant_id`; allocation percentages use `Decimal` and total exactly `Decimal("100")`; one person/employee can have only one active plaza assignment at a time; vacancy is valid and exposed without creating approval requests.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Percentage total, vacancy validity, effective-dated superior lookup, overlapping active assignment rejection. | Pure pytest against domain/service fakes before implementation. |
| Integration | Tenant-scoped repository filtering, cost-center validation rejection, audit fields. | pytest-asyncio with PostgreSQL test database once Flyway/tooling exists. |
| HTTP | HR router registration and explicit 501 scaffold behavior initially; later auth/tenant rejection. | FastAPI `TestClient`, matching current scaffold tests. |

## Migration / Rollout

Phase 1 adds import-safe contracts, route scaffolds, docs, and tests. Phase 2 adds reviewed SQL migrations for `hr_organizational_units`, `hr_plazas`, `hr_plaza_reporting_lines`, `hr_plaza_assignments`, `hr_plaza_cost_allocations`, and `accounting_cost_centers`, with foreign keys from HR allocation rows to Accounting cost centers and a uniqueness/exclusion strategy for one active assignment per person. Rollout is additive; no existing data migration is required.

## Open Questions

None.
