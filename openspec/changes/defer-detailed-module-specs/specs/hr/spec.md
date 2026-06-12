# HR Specification

## ADDED Requirements

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

HR MUST generate tenant-scoped payroll runs from approved contracts, payroll inputs, bonuses, deduction catalog definitions, and suspensions. Approved payroll totals SHALL use Decimal money semantics and UTC timestamps. HR MUST provide approved payroll payable obligations and expense summaries to Accounting through a service port, event, or integration message; HR MUST NOT write Accounting tables directly. The handoff SHALL include tenant, payroll run reference, employee or summarized counterparty references, gross amounts, deduction breakdown, net payable amount, currency, occurred_at UTC timestamp, and idempotency key.

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
