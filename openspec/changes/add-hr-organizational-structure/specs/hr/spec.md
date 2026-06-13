# Delta for HR

## ADDED Requirements

### Requirement: Organizational Units

HR MUST maintain tenant-scoped, effective-dated organizational units as HR-owned organizational master data. Units SHALL preserve UTC audit history and SHALL NOT be owned by IAM.

#### Scenario: Create effective-dated unit

- GIVEN an authorized HR user in tenant A
- WHEN the user creates unit "Finance" effective 2026-01-01
- THEN HR records the unit for tenant A with effective dates and UTC audit timestamps

#### Scenario: Cross-tenant unit access rejected

- GIVEN unit U-10 belongs to tenant A
- WHEN a tenant B principal requests U-10
- THEN HR rejects access without exposing tenant A data

### Requirement: Plazas and Reporting Hierarchy

HR MUST maintain plazas as tenant-scoped, budgeted or authorized positions independent of employee assignment. A plaza MAY be vacant. Plaza-to-plaza reporting lines SHALL be effective-dated. Future approval consumers SHOULD escalate immediately to the superior plaza when an authorization plaza is vacant; this change MUST NOT implement approval workflow execution.

#### Scenario: Vacant plaza is valid

- GIVEN tenant A has organizational unit U-10
- WHEN HR creates plaza P-10 without an assigned employee
- THEN HR records P-10 as vacant and available for authorization reference

#### Scenario: Effective-dated superior plaza

- GIVEN plazas P-10 and P-20 exist in tenant A
- WHEN HR records P-20 as P-10's superior effective 2026-02-01
- THEN hierarchy queries for that date return P-20 as the superior plaza

#### Scenario: Vacant authorization plaza escalation contract

- GIVEN plaza P-10 is vacant and reports to P-20
- WHEN a future approval consumer requests the authorization target for P-10
- THEN the consumer contract requires immediate escalation to P-20
- AND HR does not create approval requests, decisions, timers, or notifications

### Requirement: Position Assignments and Vinculation

HR MUST record person or employee assignments to plazas with effective dates and a contract or vinculation reference. For this change, a person or employee MUST NOT have more than one active plaza assignment at the same time. HR MUST NOT infer professional services as non-labor solely from its label. Concurrent assignments are out of scope and MAY be reconsidered only in a future change.

#### Scenario: Assign employee to plaza

- GIVEN employee E-10, contract C-10, and vacant plaza P-10 exist in tenant A
- WHEN HR assigns E-10 to P-10 effective 2026-03-01
- THEN HR records the assignment with contract reference and effective dates

#### Scenario: Concurrent active assignment rejected

- GIVEN E-10 already has an active plaza assignment
- WHEN HR records another plaza assignment for E-10 with an overlapping active effective period
- THEN HR rejects the assignment because only one active plaza assignment is allowed

#### Scenario: Professional services label not decisive

- GIVEN an assignment is labeled "professional services"
- WHEN HR evaluates vinculation classification
- THEN HR requires configured legal/compliance rules and does not classify it by label alone

### Requirement: Plaza Cost Allocation References

HR MAY allocate a plaza or assignment across one or more active Accounting cost centers using percentages and effective dates. HR MUST store database identifiers suitable for foreign-key relationships and expose human-readable cost center codes in contracts or read models. HR MUST validate cost center references through an Accounting boundary or read contract and MUST NOT own the cost center catalog lifecycle.

#### Scenario: Split allocation across active cost centers

- GIVEN Accounting exposes active cost centers CC-10 and CC-20 for tenant A
- WHEN HR allocates plaza P-10 as 60% CC-10 and 40% CC-20 effective 2026-04-01
- THEN HR records cost center database identifiers with percentages totaling 100%
- AND HR exposes the human-readable cost center codes in allocation read models

#### Scenario: Inactive cost center rejected

- GIVEN Accounting marks cost center CC-30 inactive
- WHEN HR references CC-30 in a new allocation
- THEN HR rejects the allocation through the boundary validation result

### Requirement: HR Organizational Audit and IAM Linkage

HR organizational structure actions MUST require IAM-provided principal, permission, and tenant scope. IAM user linkage SHALL remain via person or employee references; IAM MUST NOT own organizational units, plazas, reporting lines, assignments, or cost allocations.

#### Scenario: IAM user linked through employee

- GIVEN employee E-10 links to IAM user U-10
- WHEN HR assigns E-10 to plaza P-10
- THEN the plaza assignment remains HR-owned and IAM stores no org-structure ownership

#### Scenario: Organizational change is auditable

- GIVEN an authorized HR user updates plaza P-10
- WHEN the change is saved
- THEN HR records actor, tenant, UTC timestamp, reason when applicable, and before/after state where safe
