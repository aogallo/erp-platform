# Invoice Specification

## Purpose

Invoice domain covers invoice creation, lifecycle management, posting (with atomic inventory deduction, accounting entry, and asynchronous FEL authorization), immutability guarantees, and credit notes. It is the core transactional document.

## Requirements

### Requirement: Invoice Creation (Draft)

The system MUST allow creating invoices in "draft" status. A draft SHALL require an existing customer and at least one line item. Each line item SHALL reference a product, quantity, and unit price.

#### Scenario: Create draft invoice with valid data

- GIVEN customer ID 1 exists, product ID 5 exists (price 100.00)
- WHEN POST /invoices with customer_id 1, line_items [{product_id 5, quantity 2, unit_price 100.00}]
- THEN status 201, status "draft", total 200.00 plus tax

#### Scenario: Create invoice without line items is rejected

- GIVEN customer ID 1 exists
- WHEN POST /invoices with customer_id 1, empty line_items
- THEN status 422 — at least one line item required

### Requirement: Invoice Posting

The system MUST allow posting a draft invoice to "posted_pending_fel" status. Posting SHALL trigger a local transaction manager that atomically: records the invoice, deducts inventory, creates the accounting entry, and enqueues a FEL authorization request. External FEL authorization SHALL run asynchronously and MUST NOT roll back the local posting after it commits.

#### Scenario: Post invoice enqueues FEL authorization

- GIVEN draft invoice ID 10, product X stock 10
- WHEN POST /invoices/10/post
- THEN status changes to "posted_pending_fel", stock is reduced, accounting entry is created, and FEL authorization is queued

#### Scenario: Local posting failure rolls back local transaction

- GIVEN draft invoice ID 11 and inventory cannot be deducted
- WHEN POST /invoices/11/post
- THEN status remains "draft", no inventory is deducted, no accounting entry is created, and no FEL request is queued

### Requirement: Invoice Immutability

A posted invoice in "posted_pending_fel" or "fel_authorized" status MUST NOT be modified. Any update attempt SHALL be rejected. Corrections MUST use credit notes only.

#### Scenario: Update posted invoice rejected

- GIVEN invoice ID 20 has status "fel_authorized"
- WHEN PUT /invoices/20 with any field change
- THEN status 409 — invoice is immutable

#### Scenario: Delete posted invoice rejected

- GIVEN invoice ID 21 has status "posted_pending_fel"
- WHEN DELETE /invoices/21
- THEN status 409 — invoice is immutable

### Requirement: FEL Integration

The system MUST submit posted invoices to Infile (Guatemala FEL provider) asynchronously. The system SHALL store the confirmation UUID and mark the invoice "fel_authorized" on success. On transient failure, it SHOULD retry with exponential backoff and keep the invoice visible as "posted_pending_fel" or "fel_failed".

#### Scenario: Successful asynchronous FEL submission

- GIVEN invoice ID 30 has status "posted_pending_fel"
- WHEN the FEL worker submits it and Infile responds with a confirmation UUID
- THEN the invoice stores the UUID and FEL document number and status becomes "fel_authorized"

#### Scenario: Retry on transient failure

- GIVEN Infile returns 503 on first 2 attempts
- WHEN the adapter retries submission
- THEN it retries with backoff; if a later attempt succeeds UUID is stored; if attempts are exhausted status becomes "fel_failed"

#### Scenario: Manual FEL retry after failure

- GIVEN invoice ID 31 has status "fel_failed"
- WHEN an authorized user requests FEL retry
- THEN a new FEL authorization attempt is queued without duplicating inventory or accounting entries

### Requirement: Credit Notes

The system MUST allow creating a credit note against a FEL-authorized invoice. A credit note SHALL reverse accounting entries, restore inventory when applicable, and request the corresponding FEL credit/cancellation flow. The credited invoice SHALL have status "credited" and MUST NOT be credited again.

#### Scenario: Full credit note

- GIVEN invoice ID 40 has status "fel_authorized", amount 500.00, inventory deducted
- WHEN POST /invoices/40/credit-note with reason "Customer returned goods"
- THEN credit note for 500.00 created, inventory restored, reversing entry created, status "credited"

#### Scenario: Re-credit blocked

- GIVEN invoice ID 41 has status "credited"
- WHEN POST /invoices/41/credit-note
- THEN status 409 — invoice already credited

### Requirement: Invoice Query

The system MUST support querying by invoice number, date range, customer ID, and status. Results SHALL be paginated with default page size 20.

#### Scenario: Query by date range

- GIVEN invoices dated 2026-01-15, 2026-02-10, 2026-03-20
- WHEN GET /invoices?date_from=2026-02-01&date_to=2026-03-31
- THEN returns invoices from 2026-02-10 and 2026-03-20

#### Scenario: Query by status

- GIVEN 5 draft and 15 posted invoices
- WHEN GET /invoices?status=draft
- THEN returns only the 5 draft invoices
