# Inventory Specification

## Requirements

### Requirement: Product Master Data

The system MUST maintain tenant-scoped products used by Inventory, Sales, and Purchasing. Each product SHALL have a stable product ID, SKU, name, status, stock-tracking mode, optional unit of measure, and UTC audit timestamps. SKU uniqueness MUST be enforced per tenant. Disabled products MUST NOT be used in new Sales or Purchasing documents, but historical movements MUST remain traceable.

#### Scenario: Create a stock-tracked product

- GIVEN an authorized inventory user in tenant A
- WHEN the user creates product SKU "SKU-100" with stock_tracking enabled
- THEN the product is created for tenant A with status "active" and UTC audit timestamps

#### Scenario: Duplicate SKU rejected within tenant

- GIVEN tenant A already has product SKU "SKU-100"
- WHEN an authorized inventory user creates another active product with SKU "SKU-100" in tenant A
- THEN the request is rejected with conflict and no product is created

#### Scenario: Same SKU allowed in another tenant

- GIVEN tenant A has product SKU "SKU-100"
- WHEN tenant B creates product SKU "SKU-100"
- THEN the product is created under tenant B without exposing tenant A data

### Requirement: Warehouse Master Data

The system MUST maintain tenant-scoped warehouses as stock locations. A warehouse SHALL have a stable warehouse ID, code, name, status, and UTC audit timestamps. Warehouse codes MUST be unique per tenant. Disabled warehouses MUST NOT accept new stock movements but MUST remain available for historical queries.

#### Scenario: Create warehouse

- GIVEN an authorized inventory user in tenant A
- WHEN the user creates warehouse code "MAIN"
- THEN the warehouse is created for tenant A with status "active"

#### Scenario: Movement into disabled warehouse rejected

- GIVEN warehouse "MAIN" is disabled
- WHEN a goods receipt attempts to increase stock in warehouse "MAIN"
- THEN the movement is rejected and stock balances remain unchanged

### Requirement: Stock Balances and Availability

The system MUST calculate stock availability by tenant, product, and warehouse from accepted stock movements. Availability SHALL distinguish on-hand, reserved, and available quantities. Quantity values MUST use Decimal semantics and MUST NOT use floating point arithmetic.

#### Scenario: Query available stock

- GIVEN product SKU "SKU-100" has on-hand quantity 10 and reserved quantity 3 in warehouse "MAIN"
- WHEN Sales queries availability for the product and warehouse
- THEN Inventory returns available quantity 7 using Decimal quantity semantics

#### Scenario: Tenant isolation for availability

- GIVEN tenant A and tenant B both use product SKU "SKU-100"
- WHEN tenant A queries availability
- THEN only tenant A stock balances are returned

### Requirement: Stock Movements

The system MUST record every stock change as an immutable, tenant-scoped stock movement. A movement SHALL include product, warehouse, signed quantity, movement type, source context, source reference, occurred_at UTC timestamp, and created_by principal. Corrections MUST be represented by reversal or adjustment movements; accepted movements MUST NOT be edited in place.

#### Scenario: Record purchasing receipt movement

- GIVEN an accepted goods receipt from Purchasing for product SKU "SKU-100" quantity 5 into warehouse "MAIN"
- WHEN Inventory accepts the receipt through its application port
- THEN Inventory records an inbound stock movement and increases on-hand quantity by 5

#### Scenario: Reverse erroneous movement

- GIVEN stock movement M1 increased product SKU "SKU-100" by 5
- WHEN an authorized inventory user reverses M1 with reason "wrong warehouse"
- THEN a reversal movement is recorded and M1 remains immutable

#### Scenario: Unauthorized movement rejected

- GIVEN a principal lacks the required inventory movement permission
- WHEN the principal attempts to create an adjustment movement
- THEN the request is rejected and no movement is recorded

### Requirement: Sales Stock Coordination

Inventory MUST expose application services or ports for Sales to reserve, deduct, and restore stock during invoice and credit-note flows. Sales MUST NOT write Inventory tables directly. Stock deduction for invoice posting MUST be atomic with the local posting workflow coordinated by the application service and Unit of Work boundary.

#### Scenario: Deduct stock for posted invoice

- GIVEN a draft Sales invoice requires product SKU "SKU-100" quantity 2 and Inventory has available quantity 5
- WHEN Sales posts the invoice through the posting workflow
- THEN Inventory deducts quantity 2 and records a movement with source context "sales" and the invoice reference

#### Scenario: Insufficient stock blocks posting

- GIVEN a draft Sales invoice requires product SKU "SKU-100" quantity 8 and Inventory has available quantity 5
- WHEN Sales attempts to post the invoice
- THEN Inventory rejects the deduction, Sales keeps the invoice in draft, and no accounting or FEL side effects are committed

#### Scenario: Restore stock for credit note

- GIVEN a FEL-authorized invoice deducted product SKU "SKU-100" quantity 2
- WHEN Sales creates an accepted credit note for returned goods
- THEN Inventory records a restoring movement linked to the credit note reference

### Requirement: Purchasing Receipt Coordination

Inventory MUST accept stock increases from Purchasing goods receipts through an application port or domain event handler. Purchasing MUST provide product, warehouse, quantity, source receipt reference, and tenant scope. Inventory MUST validate active product and warehouse state before accepting the movement.

#### Scenario: Receive goods from Purchasing

- GIVEN Purchasing accepts goods receipt GR-10 for active product SKU "SKU-100" quantity 4 into active warehouse "MAIN"
- WHEN the receipt is handed off to Inventory
- THEN Inventory records the inbound movement and exposes the updated stock balance

#### Scenario: Receipt for inactive product rejected

- GIVEN product SKU "SKU-100" is disabled
- WHEN Purchasing attempts to receive quantity 4 for that product
- THEN Inventory rejects the movement and Purchasing records the receiving failure without writing Inventory data directly

### Requirement: Stock Valuation Inputs

Inventory MUST publish or expose stock valuation inputs for Accounting without owning ledger posting. Valuation inputs SHALL include tenant, product, warehouse, movement reference, quantity, unit cost when known, valuation amount as Decimal, currency when applicable, occurred_at UTC timestamp, and source reference.

#### Scenario: Publish valuation input after receipt

- GIVEN a goods receipt increases product SKU "SKU-100" by quantity 5 at unit cost 12.50
- WHEN Inventory records the inbound movement
- THEN Inventory makes a valuation input available to Accounting for amount 62.50 without creating a journal entry directly

#### Scenario: Valuation amount uses Decimal

- GIVEN a movement has quantity 3 and unit cost 0.10
- WHEN Inventory calculates valuation input
- THEN the amount is represented exactly as Decimal 0.30
