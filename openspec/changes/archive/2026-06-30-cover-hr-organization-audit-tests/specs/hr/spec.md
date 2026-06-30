# Delta for HR

## MODIFIED Requirements

### Requirement: HR Organizational Audit and IAM Linkage

HR organizational structure actions MUST require IAM-provided principal, permission, and tenant scope. IAM user linkage SHALL remain via person or employee references; IAM MUST NOT own organizational units, positions, reporting lines, assignments, or cost allocations. HR MUST record UTC audit timestamps and actor references for existing organizational creation paths. Future organizational update behavior SHALL record safe before/after audit state without exposing raw database identifiers; audit state MUST use business-readable references such as employee code and display name, contract code, organization unit code and name, and position code and title. Cost allocation audit behavior is future/spec-only for this change and SHOULD expose cost center codes and percentages rather than raw identifiers.
(Previously: Organizational audit required actor, tenant, UTC timestamp, reason when applicable, and safe before/after state, but did not define runtime UTC coverage boundaries or safe reference formats.)

#### Scenario: IAM user linked through employee

- GIVEN employee E-10 links to IAM user U-10
- WHEN HR assigns E-10 to position P-10
- THEN the position assignment remains HR-owned and IAM stores no org-structure ownership

#### Scenario: Organizational creation paths stamp UTC audit metadata

- GIVEN an authorized HR actor creates a unit, position, reporting line, or position assignment
- WHEN HR records the organizational structure change
- THEN the created record includes the actor reference and a timezone-aware UTC timestamp
- AND runtime tests verify the timestamp falls within the bounded execution window

#### Scenario: Future organizational update audit state uses safe references

- GIVEN a future HR update changes a unit, position, reporting line, or assignment
- WHEN HR records before and after audit state
- THEN audit state exposes business-readable references, not raw identifiers
- AND references include unit code/name, position code/title, employee code/display name, and contract code where applicable

#### Scenario: Future cost allocation audit state uses business-readable values

- GIVEN a future HR change updates a position or assignment cost allocation
- WHEN HR records before and after audit state
- THEN audit state exposes cost center codes and allocation percentages
- AND this change does not require runtime cost allocation audit service or schema implementation
