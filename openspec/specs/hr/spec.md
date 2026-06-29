# HR Specification

## Requirements

### Requirement: Employee Master Data

The system MUST maintain tenant-scoped employee records for workforce administration and payroll. Each employee SHALL have a stable employee ID, legal name, tax or government identifier when required, employment status, optional organizational assignment, optional linked IAM user reference, and UTC audit timestamps. Employee identifiers MUST be unique per tenant when configured as unique. Disabled or terminated employees MUST remain available for historical payroll and accounting traceability.

#### Scenario: Create employee

- GIVEN an authorized HR user in tenant A
- WHEN the user creates an employee with government identifier "EMP-100"
- THEN HR creates the employee for tenant A with active status and UTC audit timestamps

#### Scenario: Duplicate employee identifier rejected

- GIVEN tenant A already has employee identifier "EMP-100"
- WHEN an HR user creates another employee with the same unique identifier
- THEN the request is rejected with conflict and no employee is created

#### Scenario: Employee linked to IAM user remains HR-owned

- GIVEN employee E-10 needs system access
- WHEN HR stores an IAM user reference for E-10
- THEN HR keeps employee data in HR and does not own IAM credentials, roles, or sessions

### Requirement: Employment Contracts

The system MUST maintain tenant-scoped employment contracts that define compensation terms used by payroll. A contract SHALL include employee reference, status, start date, optional end date, compensation amount as Decimal, currency, pay frequency, work schedule or assignment, and UTC audit timestamps. Payroll MUST use approved contract terms and MUST NOT calculate compensation from ad hoc employee fields.

#### Scenario: Approve employment contract

- GIVEN employee E-10 exists in tenant A
- WHEN an authorized HR user approves a contract with salary 5000.00 GTQ
- THEN the contract becomes approved and the approval timestamp is recorded in UTC

#### Scenario: Overlapping active contracts rejected

- GIVEN employee E-10 has an approved active contract for January 2026
- WHEN an HR user approves another active contract for the same period
- THEN HR rejects the contract unless an explicit contract transition policy applies

#### Scenario: Payroll blocks unapproved contract

- GIVEN employee E-10 has only a draft contract
- WHEN payroll is generated for E-10
- THEN HR rejects payroll generation for that employee

### Requirement: Payroll Periods and Payroll Inputs

The system MUST support tenant-scoped payroll periods and payroll inputs used to generate payroll runs. Payroll inputs SHALL include period, employee, input type, amount or quantity as Decimal when numeric, effective date, source reference when applicable, status, created_by principal, and UTC audit timestamps. Inputs that affect approved payroll MUST NOT be edited in place; corrections MUST use reversal or adjustment inputs.

#### Scenario: Create payroll period input

- GIVEN payroll period "2026-01" is open and employee E-10 has an approved contract
- WHEN an authorized HR user records overtime quantity 8
- THEN HR records the payroll input with Decimal quantity and UTC audit timestamp

#### Scenario: Closed payroll period blocks new input

- GIVEN payroll period "2026-01" is closed
- WHEN an HR user attempts to add a bonus input for that period
- THEN HR rejects the input and payroll totals remain unchanged

#### Scenario: Correct approved payroll input

- GIVEN payroll input PI-10 affected an approved payroll run
- WHEN an authorized HR user corrects PI-10
- THEN HR records an adjustment input and keeps PI-10 immutable

### Requirement: Deduction Catalog

The system MUST maintain a tenant-scoped deduction catalog for legal and recurring payroll deductions. Each deduction definition SHALL include code, name, deduction type, legal basis when applicable, calculation method, frequency, applicability rules, status, and UTC audit timestamps. Payroll deduction logic MUST reference catalog definitions and MUST NOT hard-code legal or recurring deductions in payroll workflows.

#### Scenario: Create legal deduction definition

- GIVEN an authorized HR user in tenant A
- WHEN the user creates deduction code "SOCIAL-SEC" with monthly frequency
- THEN the deduction definition is created for tenant A with active status

#### Scenario: Disabled deduction not applied to new payroll

- GIVEN deduction code "LOAN" is disabled
- WHEN payroll is generated for a later period
- THEN HR does not apply the disabled deduction unless a historical approved input already references it

#### Scenario: Deduction amount uses Decimal

- GIVEN a deduction is calculated as 0.10 of base amount 1000.00
- WHEN payroll calculates the deduction
- THEN the deduction amount is represented exactly as Decimal 100.00

### Requirement: Bonuses, Allowances, Absences, and Suspensions

The system MUST record tenant-scoped bonuses, allowances, absences, and suspensions as explicit payroll inputs or payroll-impacting records. Each record SHALL include employee, period or effective date range, reason, amount or quantity as Decimal when applicable, approval status, created_by principal, and UTC audit timestamps. Suspensions and absences MUST affect payroll only through approved rules or inputs with audit history.

#### Scenario: Approve bonus for payroll

- GIVEN employee E-10 has an approved contract for period "2026-01"
- WHEN an authorized HR user approves bonus B-10 for amount 750.00
- THEN HR includes B-10 in the next eligible payroll run with Decimal amount

#### Scenario: Suspension reduces payroll by approved rule

- GIVEN employee E-10 has an approved unpaid suspension for two working days
- WHEN payroll is generated for the affected period
- THEN HR applies the configured suspension rule and stores the suspension source reference

#### Scenario: Unapproved bonus excluded

- GIVEN bonus B-11 is in draft status
- WHEN payroll is generated
- THEN B-11 is excluded from payroll totals

### Requirement: Payroll Runs and Accounting Handoff

HR MUST generate tenant-scoped payroll runs from approved contracts, payroll inputs, bonuses, deduction catalog definitions, and suspensions. Approved payroll totals SHALL use Decimal money semantics and UTC timestamps. HR MUST provide approved payroll payable obligations and expense summaries to Accounting through a service port, event, or integration message; HR MUST NOT write Accounting tables directly. The handoff SHALL include tenant, payroll run reference, source_reference mapped from the payroll run reference, employee or summarized counterparty references, gross_amount as Decimal, deduction breakdown, net_payable_amount as Decimal, amount as Decimal equal to net_payable_amount for Accounting payable posting, currency, due_date as a UTC date, occurred_at UTC timestamp, and idempotency key.

#### Scenario: Regenerate unapproved payroll run

- GIVEN payroll run PR-2026-01 is in draft or calculated status and has not been approved
- AND an authorized HR user changes an approved payroll input for the same period
- WHEN the user regenerates payroll run PR-2026-01
- THEN HR recalculates the payroll totals from the current approved contracts, inputs, bonuses, deductions, and suspensions
- AND HR records a new payroll calculation version with actor, UTC timestamp, reason, and previous version reference

#### Scenario: Regenerate unapproved payroll multiple times

- GIVEN payroll run PR-2026-01 has not been approved
- WHEN an authorized HR user regenerates the payroll run multiple times before approval
- THEN HR permits each regeneration and preserves the calculation version history
- AND only the latest unapproved calculation is eligible for approval

#### Scenario: Approved payroll run cannot be regenerated in place

- GIVEN payroll run PR-2026-01 is approved
- WHEN an HR user attempts to regenerate PR-2026-01 in place
- THEN HR rejects the regeneration
- AND HR requires reversal or adjustment inputs in a later payroll run to correct approved payroll

#### Scenario: Approve payroll and hand off payable obligations

- GIVEN payroll run PR-2026-01 is calculated from approved inputs
- WHEN an authorized HR user approves the payroll run
- THEN HR freezes payroll totals and emits or exposes payroll payable obligations to Accounting

#### Scenario: Duplicate payroll handoff is idempotent

- GIVEN Accounting already processed handoff key "hr:PR-2026-01:approved"
- WHEN HR retries the same handoff
- THEN Accounting returns the existing trace result and no duplicate payable or journal entry is created

#### Scenario: Accounting rejection preserves payroll trace

- GIVEN payroll run PR-2026-01 is approved for a closed accounting period
- WHEN Accounting rejects the handoff through the boundary
- THEN HR keeps payroll totals immutable and records the failed handoff for retry or operator review

### Requirement: HR Permissions, Tenant Scope, and Auditability

HR actions MUST require IAM-provided principal, permission, and tenant scope. Business rules MUST reference permissions generically and MUST NOT hard-code roles. All employee, contract, payroll input, deduction, bonus, suspension, payroll run, and accounting handoff queries MUST be tenant-scoped. HR MUST preserve audit history for payroll-affecting changes, including actor, UTC timestamp, reason when applicable, source reference, and before/after state where safe to expose.

#### Scenario: Unauthorized payroll approval rejected

- GIVEN a principal lacks the required payroll approval permission
- WHEN the principal attempts to approve payroll run PR-2026-01
- THEN HR rejects the request and no accounting handoff is emitted

#### Scenario: Cross-tenant employee access rejected

- GIVEN employee E-10 belongs to tenant A
- WHEN a principal scoped to tenant B requests E-10
- THEN the system returns not found or forbidden without exposing tenant A data

#### Scenario: Payroll audit trail available

- GIVEN payroll run PR-2026-01 includes contract C-10, bonus B-10, and deduction D-10
- WHEN an authorized HR user reviews the payroll audit trail
- THEN HR shows the source references, approving principals, and UTC timestamps used to calculate the run

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

### Requirement: Positions and Reporting Hierarchy

HR MUST maintain positions as tenant-scoped, budgeted or authorized HR positions independent of employee assignment. A position MAY be vacant. Position-to-position reporting lines SHALL be effective-dated. Future approval consumers SHOULD escalate immediately to the superior position when an authorization position is vacant; this change MUST NOT implement approval workflow execution.

#### Scenario: Vacant position is valid

- GIVEN tenant A has organizational unit U-10
- WHEN HR creates position P-10 without an assigned employee
- THEN HR records P-10 as vacant and available for authorization reference

#### Scenario: Effective-dated superior position

- GIVEN positions P-10 and P-20 exist in tenant A
- WHEN HR records P-20 as P-10's superior effective 2026-02-01
- THEN hierarchy queries for that date return P-20 as the superior position

#### Scenario: Vacant authorization position escalation contract

- GIVEN position P-10 is vacant and reports to P-20
- WHEN a future approval consumer requests the authorization target for P-10
- THEN the consumer contract requires immediate escalation to P-20
- AND HR does not create approval requests, decisions, timers, or notifications

### Requirement: Position Assignments and Vinculation

HR MUST record person or employee assignments to positions with effective dates and a contract or vinculation reference. For this change, a person or employee MUST NOT have more than one active position assignment at the same time. HR MUST NOT infer professional services as non-labor solely from its label. Concurrent assignments are out of scope and MAY be reconsidered only in a future change.

#### Scenario: Assign employee to position

- GIVEN employee E-10, contract C-10, and vacant position P-10 exist in tenant A
- WHEN HR assigns E-10 to P-10 effective 2026-03-01
- THEN HR records the assignment with contract reference and effective dates

#### Scenario: Concurrent active assignment rejected

- GIVEN E-10 already has an active position assignment
- WHEN HR records another position assignment for E-10 with an overlapping active effective period
- THEN HR rejects the assignment because only one active position assignment is allowed

#### Scenario: Professional services label not decisive

- GIVEN an assignment is labeled "professional services"
- WHEN HR evaluates vinculation classification
- THEN HR requires configured legal/compliance rules and does not classify it by label alone

### Requirement: Position Cost Allocation References

HR MAY allocate a position or assignment across one or more active Accounting cost centers using percentages and effective dates. HR MUST store database identifiers suitable for foreign-key relationships and expose human-readable cost center codes in contracts or read models. HR MUST validate cost center references through an Accounting boundary or read contract and MUST NOT own the cost center catalog lifecycle.

#### Scenario: Split allocation across active cost centers

- GIVEN Accounting exposes active cost centers CC-10 and CC-20 for tenant A
- WHEN HR allocates position P-10 as 60% CC-10 and 40% CC-20 effective 2026-04-01
- THEN HR records cost center database identifiers with percentages totaling 100%
- AND HR exposes the human-readable cost center codes in allocation read models

#### Scenario: Inactive cost center rejected

- GIVEN Accounting marks cost center CC-30 inactive
- WHEN HR references CC-30 in a new allocation
- THEN HR rejects the allocation through the boundary validation result

### Requirement: HR Organizational Audit and IAM Linkage

HR organizational structure actions MUST require IAM-provided principal, permission, and tenant scope. IAM user linkage SHALL remain via person or employee references; IAM MUST NOT own organizational units, positions, reporting lines, assignments, or cost allocations.

#### Scenario: IAM user linked through employee

- GIVEN employee E-10 links to IAM user U-10
- WHEN HR assigns E-10 to position P-10
- THEN the position assignment remains HR-owned and IAM stores no org-structure ownership

#### Scenario: Organizational change is auditable

- GIVEN an authorized HR user updates position P-10
- WHEN the change is saved
- THEN HR records actor, tenant, UTC timestamp, reason when applicable, and before/after state where safe
