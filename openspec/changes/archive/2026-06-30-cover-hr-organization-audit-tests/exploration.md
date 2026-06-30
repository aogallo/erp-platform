## Exploration: cover-hr-organization-audit-tests

### Current State
Issues #31 and #32 are open, approved follow-ups from `add-hr-organizational-structure`. #31 asks for runtime test coverage proving UTC audit timestamps on HR organizational creation paths. #32 asks for before/after audit-state coverage for organization updates, but no HR organization update use cases currently exist in code.

Current HR organization code is an in-memory/domain-service slice: dataclasses in `backend/src/hr/domain/organization.py`, command/read dataclasses in `backend/src/hr/schemas/organization.py`, and `OrganizationApplicationService` methods for create/list units, create positions, set reporting lines, assign positions, set cost allocations, and validate authorization targets. `create_organizational_unit`, `create_position`, `set_superior_position`, and `assign_position` stamp `created_at=datetime.now(UTC)` and `created_by=actor_id`; `PositionCostAllocation` has audit fields but `set_position_cost_allocation` currently does not set `created_at`/`created_by` and its command lacks `actor_id`. `OrganizationalUnit` and `Position` include `updated_at`/`updated_by`, but there are no update commands, service methods, repository methods, audit event/value objects, or before/after-state capture tests.

Existing tests cover vacancy, effective-dated superior lookup, overlapping assignments, Decimal allocation totals, inactive cost-center rejection, no approval side effects, basic service use-case exposure, and concurrent assignment rejection. They do not assert timezone-aware UTC values from service-created records and do not cover before/after audit state. `openspec/changes/add-hr-organizational-structure/specs/hr/spec.md` contains the relevant audit requirement and scenario, but the local `openspec/specs/hr/spec.md` does not yet contain the archived organizational-structure requirements. The local tree also lacks the referenced `openspec/changes/add-hr-organizational-structure/verify-report.md` and still has the prior change folder active; this exploration therefore uses the issue bodies plus current code/spec files as the source of truth.

### Affected Areas
- `backend/tests/hr/test_organization_service.py` — primary target for runtime tests around UTC audit metadata and any before/after audit behavior.
- `backend/src/hr/services/organization.py` — current source of audit timestamps; likely needs injectable clock or focused assertions tolerant of real time, and any future update/audit-state orchestration would live here.
- `backend/src/hr/domain/organization.py` — has `created_at`/`created_by` and partial `updated_at`/`updated_by` fields, but no before/after audit-state model.
- `backend/src/hr/schemas/organization.py` — creation commands carry `actor_id`; cost allocation and future update commands may need actor/reason fields.
- `backend/src/hr/repositories/contracts.py` — would need update/audit persistence contract methods if #32 implements update behavior rather than only specifying future coverage.
- `openspec/changes/add-hr-organizational-structure/specs/hr/spec.md` — relevant prior delta requirement: organizational changes record actor, tenant, UTC timestamp, reason when applicable, and before/after state where safe.
- `openspec/specs/hr/spec.md` — local main spec currently lacks the HR organizational requirements, so proposal/spec phase should verify whether local branch state is stale before writing deltas.

### Approaches
1. **One SDD change for both audit follow-ups** — Treat #31 and #32 as one audit-coverage change with two task slices: creation UTC timestamp tests first, then update before/after audit behavior once the product scope of updates is explicit.
   - Pros: Keeps one coherent audit requirement, one OpenSpec trail, shared affected files, and likely one review package if #32 stays spec/design-only or minimal.
   - Cons: #32 is not currently test-only because update behavior does not exist; combining can block or inflate #31.
   - Effort: Medium if #32 is scoped narrowly; High if full update APIs/audit persistence are required.

2. **Split into two SDD changes** — Run #31 now as a focused test-coverage change; run #32 later when HR organization update use cases and safe before/after payload rules are defined.
   - Pros: Avoids scope creep, keeps #31 small and directly implementable, and prevents inventing update behavior under a test-ticket label.
   - Cons: Leaves #32 unresolved and requires another SDD flow/artifact set.
   - Effort: Low for #31; Medium/High later for #32.

### Recommendation
Split unless the proposal phase receives an explicit product decision to implement a minimal HR organization update use case now. #31 is immediately actionable against existing create paths and should stay small. #32 depends on behavior that is absent today: which organizational records are updateable, which fields are safe to expose in before/after state, whether audit state is a returned domain object, repository record, or later persistence concern, and how reason/actor are supplied.

If the orchestrator keeps the requested single change name, constrain it as a planning/spec change that makes #31 implementable now and marks #32 as requiring explicit update-scope decisions before apply. Do not silently turn #32 into broad CRUD/update implementation.

### Risks
- Local OpenSpec state appears inconsistent with the prompt: the prior change is still under `openspec/changes/add-hr-organizational-structure/`, no local archive or verify report was found, and `openspec/specs/hr/spec.md` lacks the organizational requirements. Proposal phase should verify branch freshness before basing deltas on main specs.
- #32 can become scope creep because the code has no update use cases or audit-state persistence contract today.
- Time-dependent tests can become flaky unless the design chooses an injectable clock or robust before/after time bounds.
- `PositionCostAllocationCommand` lacks `actor_id`, so coverage for allocation audit timestamps may require command/service changes, not only tests.
- Review size is likely Low for #31 alone (<100 lines), Medium for one narrow audit change (~150-350 lines), and High (>400 lines) if update APIs, schemas, repository contracts, and audit models are added.

### Ready for Proposal
Yes, with constraints. The proposal should either split #31 and #32, or explicitly scope the combined change around the smallest auditable update behavior and ask product questions before design/apply. Recommended next phase: `sdd-propose` after resolving whether #32 is allowed to introduce update behavior now.

### Product Questions Before Proposal
- Which HR organizational record types should support update audit coverage now: organizational units, positions, reporting lines, assignments, cost allocations, or only one representative record?
- For before/after audit state, which fields are safe to expose and which must be redacted or omitted?
- Should #32 introduce actual update use cases now, or only specify tests to be added when update persistence/API work exists?
- Should cost allocation audit coverage be included even though the current command has no `actor_id` and does not stamp audit metadata?
