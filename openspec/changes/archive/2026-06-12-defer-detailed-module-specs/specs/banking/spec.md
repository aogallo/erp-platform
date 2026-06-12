# Banking Specification

## ADDED Requirements

### Requirement: Bank Accounts and Movement Concepts

The system MUST maintain tenant-scoped bank accounts and configurable bank movement concepts. A bank account SHALL include a stable bank account ID, bank name, account number or masked identifier, currency, status, optional ledger account mapping, and UTC audit timestamps. Movement concepts SHALL classify operational movements such as check, deposit, transfer, debit note, credit note, fee, interest, payment, receipt, or other configured concepts.

#### Scenario: Create bank account

- GIVEN an authorized banking user in tenant A
- WHEN the user creates bank account "OPER-001" in currency "GTQ"
- THEN the bank account is created for tenant A with status "active" and UTC audit timestamps

#### Scenario: Movement on disabled bank account rejected

- GIVEN bank account "OPER-001" is disabled
- WHEN a user attempts to record a deposit for that account
- THEN Banking rejects the movement and no accounting handoff is emitted

#### Scenario: Movement concept required

- GIVEN bank account "OPER-001" is active
- WHEN a user records a bank movement without a movement concept
- THEN the request is rejected because classification is required

### Requirement: Bank Movements

Banking MUST record tenant-scoped bank movements for checks, deposits, debit notes, credit notes, payments, receipts, transfers, fees, interest, and adjustments. Each movement SHALL include bank account, concept, direction, amount as Decimal, currency, movement date, occurred_at UTC timestamp, status, source reference when applicable, and created_by principal. Accepted movements MUST be immutable; corrections MUST use voiding, reversal, or adjustment movements.

#### Scenario: Record deposit movement

- GIVEN active bank account "OPER-001" and deposit concept "deposit"
- WHEN an authorized banking user records a deposit for amount 500.00
- THEN Banking records an inbound bank movement with Decimal amount and UTC audit timestamp

#### Scenario: Negative movement amount rejected

- GIVEN active bank account "OPER-001"
- WHEN a user attempts to save a payment movement with amount -10.00
- THEN the request is rejected and no bank movement is recorded

#### Scenario: Reverse erroneous movement

- GIVEN bank movement BM-10 was accepted for amount 100.00
- WHEN an authorized banking user reverses BM-10 with reason "duplicate import"
- THEN Banking records a reversing movement and BM-10 remains immutable

### Requirement: Checks and Print Batches

Banking MUST manage check lifecycle and print audit history. A check SHALL belong to a tenant and bank account and move through draft, printed, issued, voided, or cleared states. Printable checks MUST originate from approved payable obligations or authorized manual payment workflows and SHALL keep print batch, printed_at UTC timestamp, and printed_by principal.

#### Scenario: Print checks for approved payments

- GIVEN approved payable payment requests exist for bank account "OPER-001"
- WHEN an authorized banking user creates a check print batch
- THEN checks are marked printed, print audit history is recorded, and no check is marked cleared

#### Scenario: Void issued check before clearing

- GIVEN check CHK-10 has status "issued" and has not cleared reconciliation
- WHEN an authorized banking user voids CHK-10
- THEN the check status becomes voided and a reversal or void settlement handoff is prepared when accounting was posted

#### Scenario: Cleared check cannot be voided directly

- GIVEN check CHK-10 has status "cleared"
- WHEN a user attempts to void CHK-10
- THEN Banking rejects the request and requires an explicit correcting bank movement

### Requirement: Payments, Receipts, Deposits, and Bank Notes

Banking MUST support operational capture of payments, receipts, deposits, bank debit notes, and bank credit notes. These records SHALL create or link bank movements and SHOULD settle approved Accounting receivable or payable obligations when a settlement reference is provided. Banking owns operational settlement capture; Accounting owns ledger balances.

#### Scenario: Pay approved payable

- GIVEN Accounting exposes payable AP-10 as approved for settlement amount 62.50
- WHEN Banking records a payment from bank account "OPER-001" for AP-10
- THEN Banking records the payment movement and sends a settlement handoff to Accounting

#### Scenario: Receive customer payment

- GIVEN Accounting exposes receivable AR-10 as open amount 250.00
- WHEN Banking records a receipt for AR-10 into bank account "OPER-001"
- THEN Banking records the receipt movement and sends a settlement handoff to Accounting

#### Scenario: Bank debit note records fee

- GIVEN active bank account "OPER-001" and debit note concept "bank_fee"
- WHEN Banking records a debit note for amount 15.00
- THEN Banking creates an outbound movement and prepares the configured accounting handoff

#### Scenario: Over-settlement rejected by default

- GIVEN payable AP-10 has open amount 62.50
- WHEN Banking attempts to pay 70.00 without an approved overpayment policy
- THEN Banking rejects the payment and does not emit a settlement handoff

### Requirement: Accounting Handoff

Banking MUST coordinate ledger effects with Accounting through a service port, event, or integration message. Saving a check, deposit, debit note, credit note, payment, receipt, or posting-required bank movement SHOULD create the related accounting handoff immediately within the Banking application workflow, but Banking MUST NOT write Accounting tables directly. The handoff SHALL include tenant, bank movement reference, bank account reference, concept, amount as Decimal, currency, settlement references when present, occurred_at UTC timestamp, and idempotency key.

#### Scenario: Bank movement posts accounting entry

- GIVEN a deposit movement BM-20 requires accounting posting
- WHEN Banking accepts BM-20
- THEN Banking sends an accounting handoff containing BM-20 source reference and records the handoff trace result

#### Scenario: Duplicate accounting handoff is idempotent

- GIVEN Accounting already processed handoff key "banking:BM-20:posted"
- WHEN Banking retries the same handoff
- THEN Accounting returns the existing result and no duplicate journal entry is created

#### Scenario: Accounting rejection preserves bank movement trace

- GIVEN Banking accepts bank movement BM-21 for a closed accounting period
- WHEN Accounting rejects the handoff
- THEN Banking keeps BM-21 traceable with failed accounting status for retry or operator review

### Requirement: Bank Reconciliation

Banking MUST reconcile imported or entered bank statement lines against recorded bank movements. A reconciliation SHALL be tenant-scoped and include bank account, statement period, statement lines, matched movements, exceptions, status, reconciled_at UTC timestamp, and reconciled_by principal. Reconciliation results SHALL be shared with Accounting through the configured integration boundary when they affect settlement or reporting status.

#### Scenario: Match statement line to movement

- GIVEN bank movement BM-30 for amount 500.00 and a statement line for the same amount and reference
- WHEN an authorized banking user reconciles the statement period
- THEN BM-30 is marked matched for that reconciliation and the statement line is no longer an exception

#### Scenario: Unmatched statement line remains exception

- GIVEN a statement line has no matching bank movement
- WHEN reconciliation is processed
- THEN Banking records the line as an exception for investigation without creating an accounting entry automatically

#### Scenario: Reconciled movement cannot be edited

- GIVEN bank movement BM-30 is included in an approved reconciliation
- WHEN a user attempts to edit BM-30
- THEN Banking rejects the change and requires a reversal or adjustment workflow

### Requirement: Banking Permissions and Tenant Scope

Banking actions MUST require IAM-provided principal, permission, and tenant scope. Business rules MUST reference permissions generically and MUST NOT hard-code roles. All bank accounts, movements, checks, deposits, notes, payments, receipts, settlement handoffs, and reconciliations MUST be tenant-scoped.

#### Scenario: Unauthorized payment rejected

- GIVEN a principal lacks the required banking payment permission
- WHEN the principal attempts to approve payment for payable AP-10
- THEN the request is rejected and no bank movement or accounting handoff is created

#### Scenario: Cross-tenant bank account access rejected

- GIVEN bank account "OPER-001" belongs to tenant A
- WHEN a principal scoped to tenant B requests its movements
- THEN the system returns not found or forbidden without exposing tenant A data
