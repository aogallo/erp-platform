# Apply Progress: Deferred Detailed Module Specs

## Current Slice

| Field | Value |
|-------|-------|
| Work unit | HR + IAM detailed specs |
| PR boundary | Specification-only slice for HR and IAM; prior Inventory/Purchasing/Accounting/Banking evidence preserved |
| Chain strategy | stacked-to-main |
| Review budget | Target near/below 400 changed lines |
| Runtime changes | None |

## Completed Tasks

- [x] 1.1 Write Inventory detailed spec for products, warehouses, stock movements, valuation inputs, and Sales/Purchasing coordination.
- [x] 1.2 Write Accounting detailed spec for chart of accounts, journal entries, AR/AP, reports, and traceability from source contexts.
- [x] 1.3 Write Purchasing detailed spec for suppliers, purchase orders, goods receipts, supplier invoices, and payables handoff.
- [x] 1.4 Write HR detailed spec for employees, contracts, payroll inputs, deduction catalog, bonuses, suspensions, and accounting handoff.
- [x] 1.5 Write Banking detailed spec for bank accounts, movements, checks, deposits, debit/credit notes, payments, receipts, and reconciliation.
- [x] 1.7 Write IAM detailed spec for tenants, users, roles, permissions, sessions, RBAC checks, and tenant isolation.

## Apply Evidence

| Task | Evidence | Verification |
|------|----------|--------------|
| 1.1 | Created `openspec/changes/defer-detailed-module-specs/specs/inventory/spec.md` with ADDED requirements and Given/When/Then scenarios. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, and `openspec/specs/invoice/spec.md`. |
| 1.2 | Created `openspec/changes/defer-detailed-module-specs/specs/accounting/spec.md` with ADDED requirements and Given/When/Then scenarios. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, `openspec/specs/customer/spec.md`, `openspec/specs/invoice/spec.md`, Inventory valuation boundaries, and Purchasing payable handoff. |
| 1.3 | Created `openspec/changes/defer-detailed-module-specs/specs/purchasing/spec.md` with ADDED requirements and Given/When/Then scenarios. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, and Inventory integration boundary. |
| 1.4 | Created `openspec/changes/defer-detailed-module-specs/specs/hr/spec.md` with ADDED requirements and Given/When/Then scenarios, including payroll regeneration rules for unapproved runs and immutable approved runs. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, and Accounting payable handoff boundaries. |
| 1.5 | Created `openspec/changes/defer-detailed-module-specs/specs/banking/spec.md` with ADDED requirements and Given/When/Then scenarios. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, and Accounting AR/AP settlement boundaries. |
| 1.7 | Created `openspec/changes/defer-detailed-module-specs/specs/iam/spec.md` with ADDED requirements and Given/When/Then scenarios. | Reviewed against `docs/bounded-context.md`, `AGENTS.md`, and tenant/RBAC expectations used by all bounded contexts. |

## TDD Evidence

No runtime RED/GREEN cycle was required because this slice changes OpenSpec documentation only and does not add executable behavior.

## Remaining Tasks

- [ ] 1.6 Write Sales detailed spec extensions for quotes, orders, and conversion flows that precede invoice creation.
- [ ] 2.1 Reconcile cross-context scenarios against `docs/bounded-context.md`, `AGENTS.md`, `openspec/specs/customer/spec.md`, and `openspec/specs/invoice/spec.md`.
- [ ] 2.2 Split the work into smaller PR slices if the detailed spec diff exceeds the 400-line review budget.

## Notes

- Cross-context coordination is specified through application ports, events, or handoff messages; no direct table coupling is required.
- Money and quantities use Decimal semantics where relevant; audit and event timestamps use UTC.
