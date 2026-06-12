# Purchasing Specification

## Requirements

### Requirement: Supplier Master Data

The system MUST maintain tenant-scoped suppliers used by Purchasing and downstream payables workflows. Each supplier SHALL have a stable supplier ID, legal name, tax ID, status, optional contact fields, and UTC audit timestamps. Supplier tax ID uniqueness MUST be enforced per tenant. Disabled suppliers MUST NOT be used in new purchase orders or supplier invoices.

#### Scenario: Create supplier

- GIVEN an authorized purchasing user in tenant A
- WHEN the user creates supplier tax ID "SUP-123" with legal name "Acme Supplies"
- THEN the supplier is created for tenant A with status "active"

#### Scenario: Duplicate supplier tax ID rejected

- GIVEN tenant A already has supplier tax ID "SUP-123"
- WHEN an authorized purchasing user creates another supplier with tax ID "SUP-123"
- THEN the request is rejected with conflict

#### Scenario: Disabled supplier blocked for new order

- GIVEN supplier "SUP-123" is disabled
- WHEN a purchasing user creates a purchase order for that supplier
- THEN the request is rejected and no purchase order is created

### Requirement: Purchase Orders

The system MUST support tenant-scoped purchase orders for active suppliers. A purchase order SHALL include supplier, status, order date, line items, quantities, unit costs as Decimal, currency, totals as Decimal, and UTC audit timestamps. Purchase orders SHALL move through draft, approved, partially_received, received, cancelled, or closed states according to explicit workflow actions.

#### Scenario: Create draft purchase order

- GIVEN active supplier "SUP-123" and active product SKU "SKU-100"
- WHEN an authorized purchasing user creates a purchase order for quantity 5 at unit cost 12.50
- THEN the purchase order is created in draft status with Decimal totals

#### Scenario: Approve purchase order

- GIVEN purchase order PO-10 is in draft status with at least one line item
- WHEN an authorized purchasing user approves PO-10
- THEN PO-10 status becomes approved and the approval timestamp is recorded in UTC

#### Scenario: Cancel received purchase order rejected

- GIVEN purchase order PO-10 has status received
- WHEN a purchasing user attempts to cancel PO-10
- THEN the request is rejected and received history remains unchanged

### Requirement: Goods Receipts

The system MUST support goods receipts against approved purchase orders. A goods receipt SHALL identify the purchase order, received lines, warehouse, received quantities as Decimal, received_at UTC timestamp, and receiving principal. Accepted goods receipts MUST hand off stock increases to Inventory through a service port or event, never by direct Inventory table writes.

#### Scenario: Receive full purchase order

- GIVEN approved purchase order PO-10 has one line for product SKU "SKU-100" quantity 5
- WHEN an authorized purchasing user receives quantity 5 into warehouse "MAIN"
- THEN a goods receipt is accepted, PO-10 status becomes received, and Inventory is asked to increase stock

#### Scenario: Receive partial purchase order

- GIVEN approved purchase order PO-10 has one line for product SKU "SKU-100" quantity 5
- WHEN an authorized purchasing user receives quantity 2 into warehouse "MAIN"
- THEN a goods receipt is accepted and PO-10 status becomes partially_received

#### Scenario: Over-receipt rejected by default

- GIVEN approved purchase order PO-10 has remaining quantity 3 for product SKU "SKU-100"
- WHEN a purchasing user attempts to receive quantity 4 without an approved over-receipt policy
- THEN the request is rejected and Inventory is not called

#### Scenario: Inventory handoff failure preserves purchasing traceability

- GIVEN a goods receipt is submitted for inactive Inventory product SKU "SKU-100"
- WHEN Inventory rejects the stock increase through its application port
- THEN Purchasing records the receipt as failed or rejected with the Inventory error reference and does not write Inventory data directly

### Requirement: Supplier Invoices

The system MUST support tenant-scoped supplier invoices from active suppliers. A supplier invoice SHALL reference a supplier, invoice number, issue date, optional purchase order or goods receipt references, line amounts as Decimal, tax amounts as Decimal, currency, status, and UTC audit timestamps. Supplier invoice numbers MUST be unique per supplier and tenant.

#### Scenario: Record supplier invoice against receipt

- GIVEN goods receipt GR-10 exists for supplier "SUP-123"
- WHEN an authorized purchasing user records supplier invoice "INV-900" for the received goods
- THEN the supplier invoice is created in draft or pending_review status with Decimal totals

#### Scenario: Duplicate supplier invoice rejected

- GIVEN supplier "SUP-123" already has supplier invoice "INV-900"
- WHEN a purchasing user records another invoice "INV-900" for the same supplier
- THEN the request is rejected with conflict

#### Scenario: Supplier invoice amount mismatch requires review

- GIVEN goods receipt GR-10 totals 62.50
- WHEN supplier invoice "INV-901" is recorded for 70.00
- THEN the invoice is flagged for review and no payable handoff is emitted until approved

### Requirement: Payables Handoff

Purchasing MUST provide approved supplier invoice obligations to Accounting through a service port, event, or integration message. Purchasing owns supplier invoice capture and matching; Accounting owns accounts payable ledger records. The handoff SHALL include tenant, supplier reference, supplier invoice reference, amount as Decimal, currency, due date, tax breakdown when present, source references, and occurred_at UTC timestamp.

#### Scenario: Approve supplier invoice for payables

- GIVEN supplier invoice "INV-900" is matched and pending approval for amount 62.50
- WHEN an authorized purchasing user approves it
- THEN Purchasing emits or exposes a payable obligation to Accounting and marks the handoff trace reference

#### Scenario: Accounting failure does not mutate supplier invoice totals

- GIVEN supplier invoice "INV-900" is approved for amount 62.50
- WHEN Accounting rejects the payable handoff because the accounting period is closed
- THEN Purchasing keeps the supplier invoice amount immutable and records the handoff failure for retry or operator review

### Requirement: Purchasing Permissions and Tenant Scope

Purchasing actions MUST require IAM-provided principal, permission, and tenant scope. Business rules MUST reference permissions generically and MUST NOT hard-code roles. All supplier, purchase order, goods receipt, supplier invoice, and handoff queries MUST be tenant-scoped.

#### Scenario: Unauthorized supplier invoice approval rejected

- GIVEN a principal lacks supplier invoice approval permission
- WHEN the principal attempts to approve supplier invoice "INV-900"
- THEN the request is rejected and no payable handoff is emitted

#### Scenario: Cross-tenant purchase order access rejected

- GIVEN purchase order PO-10 belongs to tenant A
- WHEN a principal scoped to tenant B requests PO-10
- THEN the system returns not found or forbidden without exposing tenant A data
