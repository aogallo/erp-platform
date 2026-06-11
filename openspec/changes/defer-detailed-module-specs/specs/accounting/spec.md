# Accounting Specification

## ADDED Requirements

### Requirement: Chart of Accounts

The system MUST maintain a tenant-scoped chart of accounts used for ledger posting, reporting, and settlement handoffs. Each account SHALL have a stable account ID, code, name, type, normal balance, status, optional parent account, and UTC audit timestamps. Account codes MUST be unique per tenant. Disabled accounts MUST NOT be used in new journal entries but MUST remain available for historical reporting.

#### Scenario: Create ledger account

- GIVEN an authorized accounting user in tenant A
- WHEN the user creates account code "1101" with type "asset" and normal balance "debit"
- THEN the account is created for tenant A with status "active" and UTC audit timestamps

#### Scenario: Duplicate account code rejected within tenant

- GIVEN tenant A already has account code "1101"
- WHEN an accounting user creates another account with code "1101" in tenant A
- THEN the request is rejected with conflict and no account is created

#### Scenario: Disabled account blocked for posting

- GIVEN account code "1101" is disabled
- WHEN a source context requests a journal entry line using account code "1101"
- THEN Accounting rejects the posting and records the validation failure for the source workflow

### Requirement: Journal Entries

The system MUST record tenant-scoped journal entries as balanced ledger transactions. A journal entry SHALL include entry date, posting status, source context, source reference, line items, amounts as Decimal, currency when applicable, created_by principal, and UTC audit timestamps. Posted journal entries MUST balance debits and credits exactly and MUST NOT be edited in place; corrections MUST use reversal or adjusting entries.

#### Scenario: Post balanced journal entry

- GIVEN active accounts "1101" and "4101" exist in tenant A
- WHEN an authorized accounting workflow posts a journal entry with debit 100.00 and credit 100.00
- THEN the journal entry is posted with Decimal amounts and immutable line items

#### Scenario: Unbalanced journal entry rejected

- GIVEN active accounts exist for all lines
- WHEN a workflow attempts to post debit 100.00 and credit 99.99
- THEN Accounting rejects the entry and no ledger balances are updated

#### Scenario: Reverse posted journal entry

- GIVEN journal entry JE-10 is posted for amount 100.00
- WHEN an authorized accounting user reverses JE-10 with reason "source document voided"
- THEN Accounting creates a reversing entry linked to JE-10 and JE-10 remains immutable

### Requirement: Accounts Receivable Handoff

Accounting MUST accept receivable obligations from Sales through a service port, event, or integration message. Sales owns invoices and credit notes; Accounting owns receivable ledger records and balances. The handoff SHALL include tenant, customer reference, source invoice or credit-note reference, amount as Decimal, currency, due date when applicable, tax breakdown when present, occurred_at UTC timestamp, and idempotency key.

#### Scenario: Create receivable from posted invoice

- GIVEN Sales posts invoice INV-100 for customer C-10 amount 250.00
- WHEN Sales hands off the receivable obligation to Accounting
- THEN Accounting records the receivable, posts the configured journal entry, and stores the Sales source reference

#### Scenario: Duplicate receivable handoff is idempotent

- GIVEN Accounting already processed handoff key "sales:INV-100:posted"
- WHEN the same Sales handoff is received again
- THEN Accounting returns the existing trace result without duplicating receivables or journal entries

#### Scenario: Credit note reverses receivable

- GIVEN invoice INV-100 created receivable AR-10
- WHEN Sales accepts credit note CN-20 for the full amount
- THEN Accounting records a reversal or adjustment linked to AR-10 and the credit-note source reference

### Requirement: Accounts Payable Handoff

Accounting MUST accept payable obligations from Purchasing, HR, or approved expense workflows through a service port, event, or integration message. Source contexts own operational documents; Accounting owns payable ledger records and balances. The handoff SHALL include tenant, counterparty reference, source reference, amount as Decimal, currency, due date, tax or deduction breakdown when present, occurred_at UTC timestamp, and idempotency key.

#### Scenario: Create payable from supplier invoice

- GIVEN Purchasing approves supplier invoice "SUP-INV-900" for amount 62.50
- WHEN Purchasing hands off the payable obligation to Accounting
- THEN Accounting records the payable, posts the configured journal entry, and stores the Purchasing source reference

#### Scenario: Closed accounting period blocks payable posting

- GIVEN the accounting period for the payable date is closed
- WHEN a source context hands off a payable obligation for that date
- THEN Accounting rejects the posting with a period-closed error and does not mutate source context data directly

#### Scenario: HR payroll payable accepted through boundary

- GIVEN HR approves payroll obligations for period "2026-01"
- WHEN HR hands off payroll payable totals to Accounting
- THEN Accounting records payable ledger entries without owning employee compensation inputs

### Requirement: Source Traceability and Integration Boundaries

Accounting MUST preserve traceability from every ledger-impacting source document. Journal entries, receivables, payables, and settlements SHALL store tenant, source context, source reference, source event or handoff ID, and UTC received_at timestamp. Cross-context coordination MUST use application services, ports, events, or read models; Accounting MUST NOT read or write another bounded context's tables directly.

#### Scenario: Trace journal entry to Sales invoice

- GIVEN journal entry JE-20 was created from Sales invoice INV-100
- WHEN an authorized accounting user views JE-20 trace details
- THEN the response includes source context "sales", source reference "INV-100", and the handoff timestamp

#### Scenario: Direct source table coupling prohibited

- GIVEN Accounting needs customer, supplier, inventory valuation, payroll, or bank settlement details
- WHEN Accounting prepares posting or reporting data
- THEN it uses the source handoff payload, service port, event, or read model instead of direct table access

### Requirement: Financial Reports

The system MUST provide tenant-scoped financial reporting from posted Accounting records. Reports SHALL include at minimum trial balance, general ledger detail, accounts receivable aging, accounts payable aging, and source trace drill-downs. Report amounts MUST use Decimal semantics, report timestamps MUST use UTC, and queries SHALL respect IAM-provided permissions and tenant scope.

#### Scenario: Generate trial balance

- GIVEN tenant A has posted journal entries in January 2026
- WHEN an authorized accounting user requests the trial balance for January 2026
- THEN the report returns account balances whose total debits equal total credits

#### Scenario: Receivables aging excludes other tenants

- GIVEN tenant A and tenant B both have open receivables
- WHEN a tenant A accounting user requests receivables aging
- THEN only tenant A receivables are included

#### Scenario: Unauthorized report rejected

- GIVEN a principal lacks the required accounting report permission
- WHEN the principal requests the general ledger report
- THEN the request is rejected without exposing ledger data
