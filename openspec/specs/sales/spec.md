# Sales Specification

## Requirements

### Requirement: Sales Quotes

The system MUST support tenant-scoped sales quotes for active CRM customers. A quote SHALL include a stable quote ID, customer reference, status, issue date, expiry date, line items, quantities as Decimal, unit prices as Decimal, tax and total amounts as Decimal, currency, created_by principal, and UTC audit timestamps. Sales MUST validate customer references through the CRM boundary and MUST NOT read or write CRM tables directly.

#### Scenario: Create draft quote

- GIVEN an authorized Sales user in tenant A and active CRM customer C-10
- WHEN the user creates a quote with one line for product SKU "SKU-100" quantity 2 at unit price 100.00
- THEN Sales creates the quote in draft status with Decimal totals and UTC audit timestamps

#### Scenario: Quote for disabled customer rejected

- GIVEN CRM customer C-10 is disabled
- WHEN a Sales user creates a quote for C-10
- THEN Sales rejects the quote through the CRM customer validation boundary and no quote is created

#### Scenario: Cross-tenant customer reference rejected

- GIVEN customer C-10 belongs to tenant A
- WHEN a principal scoped to tenant B attempts to create a quote for C-10
- THEN Sales rejects the request without exposing tenant A customer data

### Requirement: Quote Approval and Expiry

The system MUST manage quote lifecycle states explicitly. Quotes SHALL move through draft, approved, expired, converted, or cancelled states by authorized workflow actions. Approved quote content MUST be immutable except for explicit cancellation or conversion metadata. Expired, converted, or cancelled quotes MUST NOT be converted to new sales orders.

#### Scenario: Approve quote

- GIVEN quote Q-10 is in draft status with at least one line and a future expiry date
- WHEN an authorized Sales user approves Q-10
- THEN Q-10 status becomes approved and approval actor and UTC timestamp are recorded

#### Scenario: Expired quote cannot be approved

- GIVEN quote Q-10 has an expiry date before the current UTC date
- WHEN a Sales user attempts to approve Q-10
- THEN Sales rejects the approval and Q-10 remains draft or expired according to the expiry policy

#### Scenario: Approved quote line edit rejected

- GIVEN quote Q-10 has status approved
- WHEN a Sales user attempts to change a line quantity or unit price
- THEN Sales rejects the update and preserves the approved quote content

### Requirement: Quote to Sales Order Conversion

Sales MUST convert approved, unexpired quotes into sales orders through an explicit workflow. Conversion SHALL copy customer reference, approved quote lines, Decimal prices, tax breakdown, currency, and source quote reference into the sales order. The converted quote MUST retain immutable source content and conversion audit metadata. Sales MUST coordinate stock availability or reservation with Inventory through an application port, service, event, or read model, never through direct Inventory table coupling.

#### Scenario: Convert approved quote to sales order

- GIVEN quote Q-10 is approved, unexpired, and has active line items
- WHEN an authorized Sales user converts Q-10 to a sales order
- THEN Sales creates sales order SO-10 with source quote reference Q-10 and marks Q-10 converted

#### Scenario: Convert expired quote rejected

- GIVEN quote Q-10 has status expired
- WHEN a Sales user attempts to convert Q-10
- THEN Sales rejects the conversion and no sales order is created

#### Scenario: Inventory availability boundary used during conversion

- GIVEN quote Q-10 requires product SKU "SKU-100" quantity 5
- WHEN Sales converts Q-10 and the workflow requires stock reservation
- THEN Sales checks or requests reservation through the Inventory boundary and records the reservation result without writing Inventory data directly

### Requirement: Sales Orders

The system MUST support tenant-scoped sales orders for active customers. A sales order SHALL include a stable order ID, customer reference, optional source quote reference, status, order date, line items, quantities as Decimal, unit prices as Decimal, tax and total amounts as Decimal, currency, fulfillment or reservation references when applicable, created_by principal, and UTC audit timestamps. Sales order lifecycle states SHALL include draft, confirmed, partially_fulfilled, fulfilled, invoiced, cancelled, or closed.

#### Scenario: Create draft sales order directly

- GIVEN an authorized Sales user in tenant A and active CRM customer C-10
- WHEN the user creates a sales order with one line item
- THEN Sales creates the order in draft status with Decimal totals and no invoice side effects

#### Scenario: Confirm sales order

- GIVEN sales order SO-10 is draft with valid customer and line items
- WHEN an authorized Sales user confirms SO-10
- THEN SO-10 status becomes confirmed and confirmation actor and UTC timestamp are recorded

#### Scenario: Mark sales order partially fulfilled

- GIVEN sales order SO-10 is confirmed for quantity 10 of SKU "SKU-100"
- AND Inventory reports fulfillment of quantity 4 through the fulfillment boundary
- WHEN Sales records the fulfillment trace
- THEN SO-10 status becomes partially_fulfilled
- AND Sales preserves the Inventory fulfillment reference without writing Inventory movement data directly

#### Scenario: Mark sales order fulfilled

- GIVEN sales order SO-10 is partially_fulfilled with remaining quantity 6 of SKU "SKU-100"
- AND Inventory reports fulfillment of the remaining quantity through the fulfillment boundary
- WHEN Sales records the fulfillment trace
- THEN SO-10 status becomes fulfilled
- AND the fulfilled quantities are available for invoice conversion according to invoice policy

#### Scenario: Close fulfilled and invoiced sales order

- GIVEN sales order SO-10 is fulfilled and fully invoiced
- WHEN an authorized Sales user closes SO-10
- THEN SO-10 status becomes closed
- AND Sales records closing actor, UTC timestamp, and reason without changing copied invoice terms

#### Scenario: Cancel invoiced sales order rejected

- GIVEN sales order SO-10 has status invoiced
- WHEN a Sales user attempts to cancel SO-10
- THEN Sales rejects the cancellation and preserves invoice traceability

### Requirement: Inventory Availability and Reservation Boundary

Sales MUST coordinate stock availability, reservation, release, and final deduction through Inventory application boundaries. Sales MAY store Inventory reservation references and availability snapshots for workflow traceability, but Inventory remains the source of truth for stock balances and movements. Reservations and availability quantities MUST use Decimal semantics.

#### Scenario: Reserve stock for confirmed order

- GIVEN sales order SO-10 is ready for confirmation and Inventory reports available quantity 10 for SKU "SKU-100"
- WHEN Sales confirms SO-10 for quantity 4 and reservation is required
- THEN Sales requests Inventory reservation and stores the reservation reference returned by Inventory

#### Scenario: Insufficient stock blocks reservation

- GIVEN sales order SO-10 requires quantity 8 and Inventory reports available quantity 5
- WHEN Sales attempts to reserve stock for SO-10
- THEN Sales records the Inventory rejection and SO-10 is not confirmed or remains pending according to the workflow policy

#### Scenario: Cancel order releases reservation

- GIVEN confirmed sales order SO-10 has Inventory reservation R-10
- WHEN Sales cancels SO-10 before invoicing
- THEN Sales requests reservation release through Inventory and records the release trace result

### Requirement: Sales Order to Invoice Conversion

Sales MUST create invoices from confirmed or fulfilled sales orders using the existing Invoice draft-creation and posting boundaries. Invoice creation from an order SHALL preserve source order reference, customer reference, line quantities, prices, tax breakdown, currency, and Decimal totals, and SHALL satisfy the Invoice specification requirement for an existing customer and at least one line item. Invoice posting, Inventory deduction, Accounting receivable handoff, and asynchronous FEL authorization remain governed by the Invoice specification and cross-cutting outbox boundary.

#### Scenario: Convert confirmed order to draft invoice

- GIVEN sales order SO-10 is confirmed and not fully invoiced
- WHEN an authorized Sales user creates an invoice from SO-10
- THEN Sales creates a draft invoice with source order reference SO-10, at least one line item, and keeps posting side effects pending until invoice posting

#### Scenario: Duplicate full invoice conversion rejected

- GIVEN sales order SO-10 has already been fully invoiced
- WHEN a Sales user attempts to create another full invoice from SO-10
- THEN Sales rejects the conversion and no duplicate invoice is created

#### Scenario: Invoice posting uses existing invoice boundaries

- GIVEN draft invoice INV-10 was created from sales order SO-10
- WHEN Sales posts INV-10
- THEN posting follows the Invoice specification for atomic local posting, Inventory deduction, Accounting receivable handoff, and asynchronous FEL authorization

### Requirement: Sales Credit and Customer Reference Boundary

Sales MUST validate operational customer references through CRM and MUST coordinate customer credit or receivable exposure checks through Accounting when credit policy requires it. CRM owns customer master data; Accounting owns receivable balances and credit exposure data. Sales MUST use ports, events, integration messages, or read models for these checks and MUST NOT directly couple to CRM or Accounting tables.

#### Scenario: Credit check blocks order confirmation

- GIVEN customer C-10 has credit exposure above the configured limit according to Accounting
- WHEN Sales attempts to confirm sales order SO-10 for C-10
- THEN Sales rejects or holds the confirmation according to credit policy and records the Accounting credit-check trace

#### Scenario: Accounting credit service unavailable preserves order draft

- GIVEN credit policy requires Accounting validation and the Accounting boundary is unavailable
- WHEN Sales attempts to confirm SO-10
- THEN Sales leaves SO-10 unconfirmed and records a retryable validation failure without mutating Accounting data

### Requirement: Sales Permissions, Tenant Scope, and Auditability

Sales actions MUST require IAM-provided principal, permission, and tenant scope. Business rules MUST reference permissions generically and MUST NOT hard-code roles. All quotes, orders, invoices, conversion traces, reservation references, and credit-check traces MUST be tenant-scoped. Converted documents and approved commercial terms MUST preserve immutable audit history with actor, UTC timestamp, source reference, and conversion reason when applicable.

#### Scenario: Unauthorized quote approval rejected

- GIVEN a principal lacks the required Sales quote approval permission
- WHEN the principal attempts to approve quote Q-10
- THEN Sales rejects the approval and no conversion-eligible quote state is created

#### Scenario: Cross-tenant sales order access rejected

- GIVEN sales order SO-10 belongs to tenant A
- WHEN a principal scoped to tenant B requests SO-10
- THEN Sales returns not found or forbidden without exposing tenant A data

#### Scenario: Conversion audit trail available

- GIVEN quote Q-10 was converted to sales order SO-10 and then invoice INV-10
- WHEN an authorized Sales user reviews the conversion trail
- THEN Sales shows the source document references, actors, UTC timestamps, and immutable copied commercial terms
