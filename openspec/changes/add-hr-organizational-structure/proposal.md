# Proposal: Add HR Organizational Structure

## Intent

Define HR-owned organizational structure and positions so future approval workflows can route by authorized position instead of employee identity. Today HR has optional employee assignment but no model for vacant authorization positions, reporting lines, or cost allocation.

## Scope

### In Scope
- Model tenant-scoped organizational units, positions, reporting relationships, and assignment history in HR.
- Support vacant positions; a position is a budgeted/authorized HR position and may exist without an employee.
- Allow position cost allocation across multiple active Accounting cost centers with percentages and effective dates.
- Enforce one active position assignment per person or employee for this change.

### Out of Scope
- Approval workflow engine, requests, notifications, reminders, timers, escalation decisions, or approver resolution execution.
- IAM ownership of organization structure, roles-as-positions, or hard-coded business approver roles.
- HR ownership of the Accounting/Finance cost center catalog.
- Concurrent position assignments; they may be considered later when a business opportunity requires them.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `hr`: Add organizational units, positions, position hierarchy, employee assignments, assignment compliance boundaries, and position cost allocation references.
- `accounting`: Clarify Accounting-owned cost center catalog for HR position allocations.

## Approach

Extend HR with role-independent organizational master data: units, positions, effective-dated reporting lines, assignments, and auditability. HR may correlate employees to IAM users, but IAM stays identity-only. HR references active Accounting cost centers through a boundary/read contract. Future approval workflows will consume position references; vacant authorization positions should escalate immediately to the superior position.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/hr/spec.md` | Modified | Add HR organizational structure/position requirements. |
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
- Enforcement of one active position assignment per person or employee.

## Success Criteria

- [ ] Specs define positions as HR-owned authorized positions that may be vacant.
- [ ] Specs keep IAM out of organizational ownership and Accounting as cost center owner.
- [ ] Specs preserve future approval routing by position without implementing workflows.
