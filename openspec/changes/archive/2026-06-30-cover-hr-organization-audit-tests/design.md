# Design: Cover HR Organization Audit Tests

## Technical Approach

Add focused pytest coverage around the existing HR organization creation service methods that already stamp `created_at=datetime.now(UTC)` and `created_by=actor_id`: unit creation, position creation, reporting-line creation, and position assignment. Keep #32 and cost allocation audit behavior as OpenSpec-only future requirements. This change must not add organization update commands, API routes, repository methods, audit-log storage, or cost-allocation actor/timestamp service support.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Test existing creation paths only | Add tests in `backend/tests/hr/test_organization_service.py` for the four existing creation methods. | Add a fake clock or refactor `_utc_now()` injection. | The implementation already uses UTC-aware timestamps; bounded runtime assertions prove behavior without production refactor scope. |
| Bounded UTC assertions | Capture `before = datetime.now(UTC)` immediately before the service call and `after = datetime.now(UTC)` immediately after; assert `created_at.tzinfo is UTC` and `before <= created_at <= after`. | Assert exact timestamps or only `tzinfo`. | Exact time is flaky; timezone-only misses stale/wrong instants. Bounded checks are stable and meaningful. |
| #32 future behavior | Document before/after audit-state rules in specs/design only. | Introduce update commands, services, repositories, or audit event models now. | No update use cases exist; implementing them under a test follow-up would create unapproved product scope. |
| Safe audit references | Future audit state must use business-readable values: `employee_code`/display name, `contract_code`, `unit_code`/name, and `position_code`/title. | Expose raw database IDs or opaque foreign keys. | Specs require audit state that users can understand and that avoids leaking internal identifiers. |
| Cost allocation audit | Treat runtime cost allocation audit as future/spec-only. | Add `actor_id` to `PositionCostAllocationCommand` and stamp allocation records now. | Current command lacks an actor and service does not stamp audit fields; adding support would be behavior change beyond this test-focused slice. |

## Data Flow

```text
pytest test ──command(actor_id)──→ OrganizationApplicationService
     │                                  │
     │                                  ├─ builds domain record with _utc_now()
     │                                  ├─ FakeHROrganizationRepository stores record
     │                                  └─ FakeUnitOfWork.commit()
     └─ asserts created_by and bounded UTC created_at on returned record
```

For #32, no runtime data flow is added. Future update flows should load the prior domain/read state, apply the approved update, then emit/store before/after audit state using safe business references instead of raw IDs.

## File Changes

| File | Action | Description |
|---|---|---|
| `openspec/changes/cover-hr-organization-audit-tests/design.md` | Create | Technical design for #31 runtime tests and #32/spec-only guardrails. |
| `backend/tests/hr/test_organization_service.py` | Modify later | Add pytest-asyncio tests and a small assertion helper for UTC audit metadata on existing creation paths. |
| `backend/src/hr/services/organization.py` | No change expected | Existing `_utc_now()` creation stamping remains the subject under test. |
| `backend/src/hr/schemas/organization.py` | No change | Do not add update commands or cost-allocation `actor_id` in this change. |
| `backend/src/hr/repositories/contracts.py` | No change | Do not add update/audit persistence contracts in this change. |

## Interfaces / Contracts

No new runtime interfaces are introduced. The test helper should stay test-local, for example:

```python
def assert_utc_audit(created_at: datetime | None, *, actor_id: str, before: datetime, after: datetime) -> None: ...
```

Future before/after audit contracts, when explicitly approved, must expose display-safe references rather than raw IDs: unit code/name, position code/title, employee code/display name, contract code, and cost-center code/percentage for allocation state.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit/service | `create_organizational_unit` stamps `created_by` and bounded UTC `created_at`. | pytest-asyncio with existing fake UoW/repository. |
| Unit/service | `create_position` stamps audit metadata after validating the unit. | Reuse existing fake repository seeded with a unit. |
| Unit/service | `set_superior_position` stamps audit metadata after validating both positions. | Reuse existing fake positions. |
| Unit/service | `assign_position` stamps audit metadata after assignment validation. | Reuse fake active-assignment list and assert commit occurs. |
| Spec-only | Future before/after update state and cost allocation audit references. | Covered by OpenSpec delta; no runtime tests until update/cost-allocation actor behavior exists. |
| E2E | None. | No API or UI behavior is added. |

## Migration / Rollout

No migration required. This is a test/spec follow-up with no database, API, or production behavior rollout.

## Open Questions

None. Tasks should preserve the scope guardrails: implement #31 tests only, and do not implement #32 or cost allocation runtime audit support in this change.
