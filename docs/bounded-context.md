---
name: Bounded Contexts
description: Defines domain boundaries, responsibilities, ownership, and interactions between ERP business contexts.
---

# CRM Context

Purpose:

Manage customer relationships.

Entities:

- Customer
- Contact

Responsibilities:

- Customer registration
- Customer updates
- Customer communication

API prefix: `/crm`

Relationships:

- Provides registered customers to Sales.
- Receives communication and lifecycle signals from Sales and Accounting.

---

# IAM Context

Purpose:

Manage identities, tenants, roles, permissions, and authentication sessions.

Entities:

- User
- Role
- Permission
- Tenant
- Session

Responsibilities:

- Authenticate users through a swappable provider port.
- Authorize bounded-context actions using roles and permissions.
- Enforce tenant isolation boundaries.

API prefix: `/iam`

Relationships:

- Supplies principals, permissions, and tenant scope to every context.
- Owns authentication policy; business contexts own business authorization rules.

---

# Sales Context

Purpose:

Manage sales transactions.

Entities:

- Quote
- Order
- Invoice
- Credit Note

Responsibilities:

- Create quotes
- Create orders
- Generate invoices
- Post invoices through local Unit of Work and asynchronous FEL authorization

API prefix: `/sales`

Relationships:

- Consumes CRM customer references.
- Coordinates Inventory stock deduction and Accounting journal entries during posting.
- Emits FEL authorization requests through the cross-cutting FEL/outbox boundary.

---

# Inventory Context

Purpose:

Manage products, stock, warehouses, and stock movements.

Entities:

- Product
- Warehouse
- Stock Item
- Stock Movement

Responsibilities:

- Maintain stock availability.
- Deduct and restore inventory for Sales invoices and credit notes.
- Receive stock from Purchasing.

API prefix: `/inventory`

Relationships:

- Serves stock availability to Sales.
- Receives purchase receipts from Purchasing.
- Publishes stock valuation data for Accounting.

---

# Purchasing Context

Purpose:

Manage supplier purchasing and receiving.

Entities:

- Supplier
- Purchase Order
- Goods Receipt
- Supplier Invoice

Responsibilities:

- Create purchase orders.
- Receive goods into Inventory.
- Provide payables data to Accounting.

API prefix: `/purchasing`

Relationships:

- Updates Inventory through receiving workflows.
- Sends supplier invoice obligations to Accounting and Banking.

---

# Accounting Context

Purpose:

Manage financial records.

Entities:

- Customer Account
- Journal Entry
- Account Receivable
- Account Payable

Responsibilities:

- Financial reporting
- Ledger management
- Reconciliation

API prefix: `/accounting`

Relationships:

- Receives posted Sales invoice entries and Purchasing payables.
- Provides reconciled balances to Banking.
- Does not own operational customer or inventory records.

---

# Banking Context

Purpose:

Manage bank accounts, payments, receipts, and reconciliation.

Entities:

- Bank Account
- Payment
- Receipt
- Bank Reconciliation

Responsibilities:

- Record payments and receipts.
- Reconcile bank statements.
- Coordinate settlement information with Accounting.

API prefix: `/banking`

Relationships:

- Consumes receivable/payable obligations from Accounting.
- Sends settlement and reconciliation results back to Accounting.

---

# HR Context

Purpose:

Manage employees, contracts, payroll inputs, and organizational assignments.

Entities:

- Employee
- Contract
- Department
- Payroll Period

Responsibilities:

- Maintain employee records.
- Provide payroll and expense obligations to Accounting.
- Manage role-independent organizational data.

API prefix: `/hr`

Relationships:

- Uses IAM identities when employees also access the system.
- Sends payroll accounting data to Accounting.

---

# Context Map

| Upstream | Downstream | Relationship |
|----------|------------|--------------|
| IAM | All contexts | Principal, permission, and tenant scope provider. |
| CRM | Sales | Customer master data reference. |
| Sales | Inventory | Stock deduction/restoration requests during invoice and credit-note flows. |
| Sales | Accounting | Journal-entry creation on posting and reversal. |
| Purchasing | Inventory | Goods receipts increase stock. |
| Purchasing | Accounting | Supplier invoices create payables. |
| Accounting | Banking | Payable/receivable settlement and reconciliation. |
| HR | Accounting | Payroll and employee expense obligations. |

Reports are not a bounded context yet. Reporting SHOULD consume read models or projections from the contexts above without owning transactional business rules.
