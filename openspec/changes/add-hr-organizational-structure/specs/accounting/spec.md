# Delta for Accounting

## ADDED Requirements

### Requirement: Cost Center Catalog and HR Reference Boundary

Accounting MUST own the tenant-scoped cost center catalog lifecycle for finance reporting and allocations. Each cost center SHALL have a stable database identifier, human-readable code, name, status, effective dates when applicable, and UTC audit timestamps. HR MAY reference active cost centers for plaza or assignment allocations through database relationships plus a boundary/read contract that exposes human-readable codes, but HR MUST NOT create, activate, deactivate, or otherwise own cost center catalog lifecycle.

#### Scenario: Accounting maintains cost center

- GIVEN an authorized Accounting user in tenant A
- WHEN the user creates cost center CC-10 with active status
- THEN Accounting records CC-10 with a stable database identifier as tenant A finance master data with UTC audit timestamps

#### Scenario: HR validates active cost center reference

- GIVEN Accounting exposes active cost center CC-10 for tenant A
- WHEN HR validates the cost center database identifier for a plaza allocation
- THEN Accounting returns a valid active reference with code CC-10 without exposing direct table access

#### Scenario: HR cannot own catalog lifecycle

- GIVEN HR needs a new cost center for an allocation
- WHEN HR attempts to create or activate the cost center directly
- THEN the action is rejected or routed to Accounting ownership

#### Scenario: Inactive cost center blocked for new HR allocation

- GIVEN Accounting marks cost center CC-20 inactive
- WHEN HR validates CC-20 for a new allocation
- THEN Accounting returns an inactive result and HR must reject the reference
