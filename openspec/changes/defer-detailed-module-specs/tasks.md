# Tasks: Deferred Detailed Module Specs

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 700-1,400 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Inventory/Purchasing -> Accounting/Banking -> HR/IAM -> Sales extensions |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

## Phase 1: Spec Authoring

- [ ] 1.1 Write Inventory detailed spec for products, warehouses, stock movements, valuation inputs, and Sales/Purchasing coordination.
- [ ] 1.2 Write Accounting detailed spec for chart of accounts, journal entries, AR/AP, reports, and traceability from source contexts.
- [ ] 1.3 Write Purchasing detailed spec for suppliers, purchase orders, goods receipts, supplier invoices, and payables handoff.
- [ ] 1.4 Write HR detailed spec for employees, contracts, payroll inputs, deduction catalog, bonuses, suspensions, and accounting handoff.
- [ ] 1.5 Write Banking detailed spec for bank accounts, movements, checks, deposits, debit/credit notes, payments, receipts, and reconciliation.
- [ ] 1.6 Write Sales detailed spec extensions for quotes, orders, and conversion flows that precede invoice creation.
- [ ] 1.7 Write IAM detailed spec for tenants, users, roles, permissions, sessions, RBAC checks, and tenant isolation.

## Phase 2: Consistency Review

- [ ] 2.1 Reconcile cross-context scenarios against `docs/bounded-context.md`, `AGENTS.md`, `openspec/specs/customer/spec.md`, and `openspec/specs/invoice/spec.md`.
- [ ] 2.2 Split the work into smaller PR slices if the detailed spec diff exceeds the 400-line review budget.
