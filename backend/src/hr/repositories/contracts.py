"""Repository contracts for HR organizational structure persistence."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from hr.domain.organization import (
    OrganizationalUnit,
    Position,
    PositionAssignment,
    PositionCostAllocation,
    PositionReportingLine,
)

OrganizationalUnitRecord = OrganizationalUnit
PositionRecord = Position
PositionReportingLineRecord = PositionReportingLine
PositionAssignmentRecord = PositionAssignment
PositionCostAllocationRecord = PositionCostAllocation


class HROrganizationRepository(Protocol):
    """Persistence contract for tenant-scoped HR organizational master data."""

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

    async def add_position(self, position: PositionRecord) -> PositionRecord:
        """Persist a position and return the stored record."""

    async def get_position(
        self, *, tenant_id: str, position_id: int
    ) -> PositionRecord | None:
        """Return a tenant-scoped position by ID."""

    async def list_positions(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[PositionRecord]:
        """Return tenant-scoped positions for an effective date."""

    async def add_reporting_line(
        self, reporting_line: PositionReportingLineRecord
    ) -> PositionReportingLineRecord:
        """Persist an effective-dated position reporting line."""

    async def list_reporting_lines(
        self, *, tenant_id: str, position_id: int
    ) -> list[PositionReportingLineRecord]:
        """Return tenant-scoped reporting lines for a position."""

    async def add_assignment(
        self, assignment: PositionAssignmentRecord
    ) -> PositionAssignmentRecord:
        """Persist an effective-dated position assignment."""

    async def list_active_assignments(
        self, *, tenant_id: str, employee_id: int | None, person_id: int | None
    ) -> list[PositionAssignmentRecord]:
        """Return active assignments used to enforce one active position assignment."""

    async def replace_cost_allocations(
        self, *, position_id: int, allocations: list[PositionCostAllocationRecord]
    ) -> list[PositionCostAllocationRecord]:
        """Replace cost-center allocations for a position."""
