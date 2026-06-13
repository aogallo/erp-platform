"""Repository contracts for HR organizational structure persistence."""

from __future__ import annotations

from datetime import date
from typing import Protocol


OrganizationalUnitRecord = object
PlazaRecord = object
PlazaReportingLineRecord = object
PlazaAssignmentRecord = object
PlazaCostAllocationRecord = object


class HROrganizationRepository(Protocol):
    """Persistence port for tenant-scoped HR organizational master data."""

    async def add_organizational_unit(
        self, unit: OrganizationalUnitRecord
    ) -> OrganizationalUnitRecord:
        """Persist an organizational unit and return the stored record."""

    async def get_organizational_unit(
        self, *, tenant_id: str, unit_id: int
    ) -> OrganizationalUnitRecord | None:
        """Return a tenant-scoped organizational unit by ID."""

    async def list_organizational_units(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[OrganizationalUnitRecord]:
        """Return tenant-scoped organizational units for an effective date."""

    async def add_plaza(self, plaza: PlazaRecord) -> PlazaRecord:
        """Persist a plaza and return the stored record."""

    async def get_plaza(self, *, tenant_id: str, plaza_id: int) -> PlazaRecord | None:
        """Return a tenant-scoped plaza by ID."""

    async def list_plazas(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[PlazaRecord]:
        """Return tenant-scoped plazas for an effective date."""

    async def add_reporting_line(
        self, reporting_line: PlazaReportingLineRecord
    ) -> PlazaReportingLineRecord:
        """Persist an effective-dated plaza reporting line."""

    async def add_assignment(
        self, assignment: PlazaAssignmentRecord
    ) -> PlazaAssignmentRecord:
        """Persist an effective-dated plaza assignment."""

    async def list_active_assignments(
        self, *, tenant_id: str, employee_id: int | None, person_id: int | None
    ) -> list[PlazaAssignmentRecord]:
        """Return active assignments used to enforce one active plaza assignment."""

    async def replace_cost_allocations(
        self, *, plaza_id: int, allocations: list[PlazaCostAllocationRecord]
    ) -> list[PlazaCostAllocationRecord]:
        """Replace cost-center allocations for a plaza."""
