# Design: Deferred Detailed Module Specs

## Technical Approach

This is a planning/specification change only. It should produce reviewable module specs before any new business implementation is attempted.

## Spec Authoring Rules

| Rule | Decision |
|------|----------|
| Canonical boundaries | Follow `docs/bounded-context.md` and do not create new bounded contexts without a separate architecture decision. |
| Scenario style | Use Given/When/Then scenarios and RFC 2119 keywords. |
| Integration boundaries | Describe cross-context coordination through services, ports, events, or read models; do not require direct table coupling. |
| Permissions | Reference IAM permissions generically; do not hard-code roles into business rules. |
| Money and time | Use `Decimal` semantics for money and UTC timestamps. |
| Implementation | No backend, frontend, migrations, or business logic in this follow-up until specs are accepted. |

## Planned Spec Files

| Context | Planned OpenSpec path | Primary topics |
|---------|-----------------------|----------------|
| Inventory | `openspec/changes/defer-detailed-module-specs/specs/inventory/spec.md` | Products, warehouses, stock, movements, valuation inputs. |
| Accounting | `openspec/changes/defer-detailed-module-specs/specs/accounting/spec.md` | Chart of accounts, journal entries, AR/AP, reporting, traceability. |
| Purchasing | `openspec/changes/defer-detailed-module-specs/specs/purchasing/spec.md` | Suppliers, purchase orders, goods receipts, supplier invoices. |
| HR | `openspec/changes/defer-detailed-module-specs/specs/hr/spec.md` | Employees, contracts, payroll inputs, deductions, bonuses, suspensions. |
| Banking | `openspec/changes/defer-detailed-module-specs/specs/banking/spec.md` | Bank accounts, movements, checks, deposits, notes, payments, reconciliation. |
| Sales | `openspec/changes/defer-detailed-module-specs/specs/sales/spec.md` | Quotes, orders, transitions to invoice creation. |
| IAM | `openspec/changes/defer-detailed-module-specs/specs/iam/spec.md` | Tenants, users, roles, permissions, sessions, tenant isolation. |

## Review Boundary

Keep spec authoring reviewable. If the detailed specs exceed the 400-line review budget, split by context or related context pair instead of bundling every module into one PR.
