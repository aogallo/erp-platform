# Customer Specification

## Purpose

Customer domain covers client registration, profile management, contact tracking, and lifecycle. Customers are a dependency of Invoices — no invoice without a registered customer.

## Requirements

### Requirement: Customer Registration

The system MUST allow creating a customer with name, tax_id, email (optional), and phone (optional). tax_id MUST be unique. The system SHALL return the created customer with a generated ID.

#### Scenario: Create customer with valid fields

- GIVEN no customer exists with tax_id "CF-123456-7"
- WHEN POST /customers with name "Acme Corp", tax_id "CF-123456-7", email "<contact@acme.com>"
- THEN status 201 with the customer ID and name

#### Scenario: Duplicate tax_id returns conflict

- GIVEN a customer exists with tax_id "CF-123456-7"
- WHEN POST /customers with the same tax_id
- THEN status 409 with duplicate tax_id error

#### Scenario: Missing name returns validation error

- GIVEN no preexisting customer
- WHEN POST /customers without the name field
- THEN status 422 with missing required field error

### Requirement: Customer Updates

The system MUST allow updating name, email, and phone. tax_id MUST NOT be modifiable after creation. Partial updates SHALL be supported.

#### Scenario: Update email and phone

- GIVEN customer ID 1 with email "<old@acme.com>", phone "+50255550001"
- WHEN PUT /customers/1 with email "<new@acme.com>", phone "+50255550002"
- THEN status 200 with updated fields, name unchanged

#### Scenario: tax_id modification rejected

- GIVEN customer ID 1 with tax_id "CF-123456-7"
- WHEN PUT /customers/1 with tax_id "CF-999999-9"
- THEN status 422 — tax_id is immutable

### Requirement: Customer Search

The system MUST support searching by name (partial), tax_id (exact), and email (partial). Results SHALL be paginated with default page size 20.

#### Scenario: Search by name fragment

- GIVEN "Acme Corp" and "Acme International" exist
- WHEN GET /customers?name=Acme
- THEN both customers are returned

#### Scenario: Paginated results

- GIVEN 50 customers exist
- WHEN GET /customers?page=2&page_size=20
- THEN 20 customers returned with total count 50

### Requirement: Customer Disable

The system MUST support soft-deleting customers. A disabled customer SHALL NOT be usable when creating invoices. Disabled customers SHALL NOT appear in default search results.

#### Scenario: Disable a customer

- GIVEN customer ID 1 with status "active"
- WHEN DELETE /customers/1
- THEN status changes to "disabled", excluded from search

#### Scenario: Invoice blocked for disabled customer

- GIVEN customer ID 1 is disabled
- WHEN creating an invoice referencing customer ID 1
- THEN status 409 — customer is disabled

### Requirement: Customer Contacts

The system MUST allow adding multiple contacts per customer. Each contact SHALL have name, email, phone, and optional is_primary flag. At most one contact MAY be primary.

#### Scenario: Add primary contact

- GIVEN customer ID 1 with no contacts
- WHEN POST /customers/1/contacts with name "John Doe", email "<john@acme.com>", is_primary true
- THEN status 201, contact listed as primary

#### Scenario: Remove contact

- GIVEN customer ID 1 has contact ID 5
- WHEN DELETE /customers/1/contacts/5
- THEN status 204, contact no longer associated
