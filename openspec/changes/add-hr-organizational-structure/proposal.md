# Proposal: Add HR Organizational Structure

## Intent

Define HR-owned organizational structure and plazas so future approval workflows can route by authorized position instead of employee identity. Today HR has optional employee assignment but no model for vacant authorization positions, reporting lines, or cost allocation.

## Scope

### In Scope
- Model tenant-scoped organizational units, plazas, reporting relationships, and assignment history in HR.
- Support vacant plazas; a plaza is a budgeted/authorized position and may exist without an employee.
- Allow plaza cost allocation across multiple active Accounting cost centers with percentages and effective dates.
- Enforce one active plaza assignment per person or employee for this change.

### Out of Scope
- Approval workflow engine, requests, notifications, reminders, timers, escalation decisions, or approver resolution execution.
- IAM ownership of organization structure, roles-as-positions, or hard-coded business approver roles.
- HR ownership of the Accounting/Finance cost center catalog.
- Concurrent plaza assignments; they may be considered later when a business opportunity requires them.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `hr`: Add organizational units, plazas, plaza hierarchy, employee assignments, assignment compliance boundaries, and plaza cost allocation references.
- `accounting`: Clarify Accounting-owned cost center catalog for HR plaza allocations.

## Approach

Extend HR with role-independent organizational master data: units, plazas, effective-dated reporting lines, assignments, and auditability. HR may correlate employees to IAM users, but IAM stays identity-only. HR references active Accounting cost centers through a boundary/read contract. Future approval workflows will consume plaza references; vacant authorization plazas should escalate immediately to the superior plaza.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/hr/spec.md` | Modified | Add HR organizational structure/plaza requirements. |
| `openspec/specs/accounting/spec.md` | Modified | Add cost center catalog ownership/reference requirement. |
| `docs/bounded-context.md` | Modified | Align context ownership if needed. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Employment classification is over-inferred from contract label | Med | Require compliance rules and avoid legal classification from label alone. |
| Cost center ownership leaks into HR | Med | Specify HR stores references only; Accounting owns catalog lifecycle. |
| Approval workflow scope creeps into this change | Med | Keep resolver/runtime behavior deferred to `business-approval-workflows`. |

## Rollback Plan

Before implementation, remove this change folder. After implementation, revert HR organizational artifacts and Accounting cost-center reference changes in one rollback PR.

## Dependencies

- Existing IAM principal, permission, and tenant-scope contract.
- Accounting-owned active cost center catalog/reference contract.
- Enforcement of one active plaza assignment per person or employee.

## Success Criteria

- [ ] Specs define plazas as HR-owned authorized positions that may be vacant.
- [ ] Specs keep IAM out of organizational ownership and Accounting as cost center owner.
- [ ] Specs preserve future approval routing by plaza without implementing workflows.
