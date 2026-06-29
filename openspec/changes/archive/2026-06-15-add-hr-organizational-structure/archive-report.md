# Archive Report: Add HR Organizational Structure

**Change**: add-hr-organizational-structure
**Project**: erp-platform
**Archived on**: 2026-06-15
**Status**: accepted-with-warnings
**Artifact store**: OpenSpec

## Archive Decision

Archive is accepted with warnings. The latest `sdd-verify` verdict is **PASS WITH WARNINGS**, contains no CRITICAL issues, and the user explicitly accepted the non-critical audit-depth warnings before archive.

## Gates

| Gate | Result | Evidence |
|---|---|---|
| Task completion | PASS | `tasks.md` has 17/17 implementation tasks checked and no unchecked implementation tasks. |
| Critical verification issues | PASS | `verify-report.md` lists `### CRITICAL` as `None.` |
| Warning acceptance | PASS WITH WARNINGS | User accepted audit-depth warnings and requested archive. |

## Specs Synced

| Domain | Canonical spec | Delta action | Requirements synced |
|---|---|---|---|
| HR | `openspec/specs/hr/spec.md` | ADDED | Organizational Units; Positions and Reporting Hierarchy; Position Assignments and Vinculation; Position Cost Allocation References; HR Organizational Audit and IAM Linkage |
| Accounting | `openspec/specs/accounting/spec.md` | ADDED | Cost Center Catalog and HR Reference Boundary |

## Accepted Warnings and Follow-Up Tracking

- Warning: UTC audit timestamp depth for HR organizational structure is partially evidenced. Follow-up: #31 `test(hr): cover UTC audit timestamps for organizational structure`.
- Warning: Before/after audit state for organizational updates is partially evidenced. Follow-up: #32 `test(hr): cover before-after audit state for organization updates`.
- Coverage metrics could not be produced because no coverage tool is installed; this was recorded in `verify-report.md` and does not block this accepted-with-warnings archive.

## Archive Contents Expected

- `proposal.md`
- `specs/hr/spec.md`
- `specs/accounting/spec.md`
- `design.md`
- `tasks.md`
- `apply-progress.md`
- `verify-report.md`
- `archive-report.md`

## Source of Truth Updated

The canonical OpenSpec source of truth now reflects this change in:

- `openspec/specs/hr/spec.md`
- `openspec/specs/accounting/spec.md`

## Risks

Canonical specs now include full audit semantics while current runtime tests partially evidence UTC timestamp and before/after update audit behavior. This is accepted as deferred audit-depth verification tracked by issues #31 and #32.
