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
- Cost Center

Responsibilities:

- Financial reporting
- Ledger management
- Reconciliation
- Own the cost center catalog lifecycle for finance reporting and allocation references.

API prefix: `/accounting`

Relationships:

- Receives posted Sales invoice entries and Purchasing payables.
- Provides reconciled balances to Banking.
- Exposes active cost center references to HR through a boundary/read contract.
- Does not own operational customer or inventory records.

---

# Banking Context

Purpose:

Manage bank accounts, operational bank movements, checks, deposits, debit/credit notes, payments, receipts, and reconciliation.

Entities:

- Bank Account
- Bank Movement
- Bank Movement Concept
- Check
- Check Print Batch
- Deposit
- Bank Debit Note
- Bank Credit Note
- Payment
- Receipt
- Bank Reconciliation

Responsibilities:

- Record bank account movements, including checks, deposits, debit notes, credit notes, payments, and receipts.
- Support movement capture by selected bank account and movement concept.
- Manage check lifecycle, including issuance, voiding, and print batches.
- Generate the accounting entry when a bank movement is saved and the movement requires posting.
- Reconcile bank statements.
- Coordinate settlement information with Accounting.

API prefix: `/banking`

Relationships:

- Consumes receivable/payable obligations from Accounting.
- Sends settlement and reconciliation results back to Accounting.

Key Rules:

- Banking owns operational movement history for bank accounts.
- Bank movements MUST be classified by concept, such as check, debit note, credit note, deposit, transfer, fee, interest, or other configured concepts.
- Saving a check, debit note, credit note, deposit, payment, or receipt SHOULD create the related accounting journal entry immediately through Accounting.
- Accounting entries generated from Banking MUST keep a traceable reference to the source bank movement.
- Checks MUST have a lifecycle (`draft`, `printed`, `issued`, `voided`, `cleared`) before reconciliation.
- Printable checks MUST be generated from approved payment obligations and keep print audit history.
- Debit notes, credit notes, deposits, payments, and receipts MUST produce accounting settlement events.
- Bank reconciliation MUST compare imported/entered bank statement lines against recorded bank movements and their accounting status.

---

# HR Context

Purpose:

Manage employees, contracts, payroll inputs, deductions, bonuses, suspensions, and organizational assignments.

Entities:

- Employee
- Contract
- Organizational Unit
- Plaza
- Plaza Reporting Line
- Plaza Assignment
- Plaza Cost Allocation
- Payroll Period
- Payroll Run
- Deduction Catalog
- Bonus
- Suspension

Responsibilities:

- Maintain employee records.
- Maintain employment contracts and compensation terms used to calculate payroll.
- Manage payroll runs based on contract terms, bonuses, legal deductions, recurring deductions, and suspensions.
- Maintain a deduction catalog with frequency, legal basis, applicability, and calculation method.
- Record employee bonuses, allowances, absences, and suspensions that affect payroll.
- Provide payroll and expense obligations to Accounting.
- Manage role-independent organizational units, plazas, reporting lines, assignments, and cost allocation references.

API prefix: `/hr`

Relationships:

- Uses IAM identities when employees also access the system.
- Sends approved payroll accounting data to Accounting.
- References Accounting-owned cost centers for plaza or assignment allocations without owning the cost center catalog lifecycle.

Key Rules:

- Payroll MUST be generated from approved employee contracts and payroll-period inputs.
- Legal deductions and recurring deductions MUST come from the deduction catalog, not hard-coded payroll logic.
- Suspensions, absences, and bonuses MUST be explicit payroll inputs with audit history.
- Accounting receives approved payroll obligations; HR owns payroll calculation inputs and employee compensation records.
- Organizational units, plazas, reporting lines, assignments, and allocation records are HR-owned organizational master data; IAM supplies identity, permissions, and tenant scope only.
- Plazas MAY be vacant and remain valid authorization positions for future workflow consumers.
- HR stores cost center database identifiers for allocations and exposes human-readable Accounting cost center codes through contracts or read models.

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
| Accounting | HR | Active cost center validation/read boundary for HR plaza and assignment allocations. |

Reports are not a bounded context yet. Reporting SHOULD consume read models or projections from the contexts above without owning transactional business rules.
