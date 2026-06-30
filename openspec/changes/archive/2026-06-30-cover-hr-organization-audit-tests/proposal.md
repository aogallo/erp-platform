# Proposal: Cover HR Organization Audit Tests

## Intent

Close follow-up audit gaps: prove existing HR organization creation paths stamp UTC audit metadata, and specify future before/after update audit behavior without implementing updates now.

## Scope

### In Scope
- Runtime tests for UTC `created_at`/`created_by` on unit, position, reporting-line, and assignment creation.
- Cost allocation audit coverage, or explicit documentation of the current actor/timestamp gap.
- HR spec delta for future before/after update audit behavior.
- First-slice audit-state policy using user-understandable values/codes, not raw IDs.

### Out of Scope
- Organization update commands, APIs, repositories, persistence, or UI.
- Full audit log storage/event modeling.
- IAM ownership or Accounting cost-center lifecycle changes.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `hr`: strengthen organizational audit requirements for UTC creation coverage and future safe before/after state.

## Approach

Use one narrow audit-coverage change. Specs should modify/add HR audit scenarios even though local `openspec/specs/hr/spec.md` may not yet include archived organizational requirements. Tests should assert UTC timestamps within bounded runtime windows for existing creation methods. #32 remains specification-only. First-slice safe fields: unit `name`, effective dates; position `code`, `title`, unit display name/code, effective dates; reporting line position codes/titles; assignment employee/person business reference, contract/vinculation reference, effective dates; cost allocation cost-center codes and percentages.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/changes/cover-hr-organization-audit-tests/specs/hr/spec.md` | New | Audit delta. |
| `backend/tests/hr/test_organization_service.py` | Modified later | UTC tests. |
| `backend/src/hr/schemas/organization.py` | Possible later | Allocation lacks `actor_id`. |
| `backend/src/hr/services/organization.py` | Possible later | Allocation lacks audit stamps. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| #32 expands into update implementation | Med | Keep proposal/spec explicit: future behavior only. |
| Flaky time tests | Med | Use bounded runtime assertions. |
| OpenSpec archive state is stale | Med | Reconcile HR spec with prior delta. |
| Cost allocation cannot pass audit tests as-is | High | Document gap or add minimal support only if later approved. |

## Rollback Plan

Revert this change folder's artifacts and later test-only changes. No migration/runtime rollback is expected unless later phases approve cost-allocation audit support.

## Dependencies

- Issues #31/#32 and prior `add-hr-organizational-structure` delta.

## Success Criteria

- [ ] #31 is constrained to runtime UTC tests for existing creation paths.
- [ ] #32 is constrained to future safe before/after audit specification.
- [ ] Cost allocation audit gap is carried forward.
- [ ] Remaining before/after field decisions are visible before spec/design.

## Remaining Decisions Before Specs

- Should cost allocation audit stay spec-only until `actor_id` exists, or allow minimal service changes later?
- What exact employee/person/contract display references should before/after state use?
