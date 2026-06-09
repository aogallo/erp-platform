# Proposal: Deferred Detailed Module Specs

## Intent

Create a dedicated follow-up OpenSpec change for the bounded contexts whose detailed behavior was intentionally deferred from the foundation/scaffold slice.

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Detailed behavior specs for Inventory, Accounting, Purchasing, HR, Banking, Sales, and IAM | Business logic implementation |
| Cross-context scenario alignment with CRM customers and Sales invoices | Backend/frontend scaffold changes |
| Given/When/Then scenarios, invariants, permissions, and integration boundaries per module | Database migrations or provider SDK integration |

## Approach

Author the missing module specs as OpenSpec delta specs, one bounded-context capability at a time. Use `docs/bounded-context.md`, `AGENTS.md`, existing `openspec/specs/customer/spec.md`, and existing `openspec/specs/invoice/spec.md` as the canonical references.

The follow-up should preserve the current foundation boundary: this change plans the detailed specs; implementation remains in later module-specific changes after the specs are reviewed.

## Success Criteria

- [ ] Inventory detailed spec defines products, warehouses, stock movements, valuation inputs, Sales deductions/restorations, and Purchasing receipts.
- [ ] Accounting detailed spec defines chart of accounts, journal entries, AR/AP, reporting boundaries, and source traceability from Sales, Purchasing, Banking, and HR.
- [ ] Purchasing detailed spec defines suppliers, purchase orders, goods receipts, supplier invoices, and payables handoff.
- [ ] HR detailed spec defines employees, contracts, payroll inputs, deduction catalog, bonuses, suspensions, and accounting handoff.
- [ ] Banking detailed spec defines accounts, movements, checks, deposits, debit/credit notes, payments, receipts, and reconciliation.
- [ ] Sales detailed spec extends beyond invoices to quotes, orders, and lifecycle transitions that lead to invoice creation.
- [ ] IAM detailed spec defines tenants, users, roles, permissions, sessions, RBAC checks, and tenant isolation.

## Rollback Plan

Delete this follow-up OpenSpec change directory before archive if the team chooses to split the work into smaller independent changes instead.
