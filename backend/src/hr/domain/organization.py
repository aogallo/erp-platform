"""Pure domain rules for HR organizational structure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Iterable


ALLOCATION_TOTAL_PERCENT = Decimal("100")


class AllocationTotalError(ValueError):
    """Raised when position cost allocations do not total exactly 100%."""


class VinculationType(StrEnum):
    """Configured vinculation category for position assignments."""

    EMPLOYEE = "employee"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class OrganizationalUnit:
    """Tenant-scoped HR organizational unit."""

    id: int
    tenant_id: str
    name: str
    effective_from: date
    effective_to: date | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    def is_effective_on(self, on_date: date) -> bool:
        """Return whether the unit is effective on the requested date."""
        return _date_range_contains(self.effective_from, self.effective_to, on_date)


@dataclass(frozen=True, slots=True)
class Position:
    """Budgeted or authorized HR position that may be vacant."""

    id: int
    tenant_id: str
    organizational_unit_id: int
    code: str
    title: str
    effective_from: date
    effective_to: date | None = None
    assigned_employee_id: int | None = None
    assigned_person_id: int | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    @property
    def is_vacant(self) -> bool:
        """Return whether the position currently has no direct assignment reference."""
        return self.assigned_employee_id is None and self.assigned_person_id is None

    def is_effective_on(self, on_date: date) -> bool:
        """Return whether the position is effective on the requested date."""
        return _date_range_contains(self.effective_from, self.effective_to, on_date)


@dataclass(frozen=True, slots=True)
class PositionReportingLine:
    """Effective-dated superior relationship between two positions."""

    tenant_id: str
    position_id: int
    superior_position_id: int
    effective_from: date
    effective_to: date | None = None
    created_at: datetime | None = None
    created_by: str | None = None

    def is_effective_on(self, on_date: date) -> bool:
        """Return whether the reporting line is effective on the requested date."""
        return _date_range_contains(self.effective_from, self.effective_to, on_date)


@dataclass(frozen=True, slots=True)
class PositionAssignment:
    """Effective-dated assignment of a person or employee to a position."""

    tenant_id: str
    position_id: int
    employee_id: int | None
    person_id: int | None
    contract_id: int
    effective_from: date
    effective_to: date | None = None
    vinculation_type: VinculationType | None = None
    vinculation_reference: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None

    def overlaps(self, other: PositionAssignment) -> bool:
        """Return whether this assignment overlaps another effective period."""
        return _date_ranges_overlap(
            self.effective_from,
            self.effective_to,
            other.effective_from,
            other.effective_to,
        )


@dataclass(frozen=True, slots=True)
class PositionCostAllocation:
    """HR reference to an Accounting-owned cost center allocation."""

    tenant_id: str
    position_id: int
    cost_center_id: int
    percentage: Decimal
    effective_from: date
    effective_to: date | None = None
    cost_center_code: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None

    def is_effective_on(self, on_date: date) -> bool:
        """Return whether the allocation is effective on the requested date."""
        return _date_range_contains(self.effective_from, self.effective_to, on_date)


def find_effective_superior_position_id(
    reporting_lines: Iterable[PositionReportingLine],
    *,
    tenant_id: str,
    position_id: int,
    on_date: date,
) -> int | None:
    """Return the effective superior position ID for a position and date."""
    matching_lines = [
        line
        for line in reporting_lines
        if line.tenant_id == tenant_id
        and line.position_id == position_id
        and line.is_effective_on(on_date)
    ]
    if not matching_lines:
        return None

    effective_line = max(matching_lines, key=lambda line: line.effective_from)
    return effective_line.superior_position_id


def has_overlapping_assignment(
    existing_assignments: Iterable[PositionAssignment],
    proposed_assignment: PositionAssignment,
) -> bool:
    """Return whether a person or employee already has an overlapping assignment."""
    return any(
        _same_assignee(existing_assignment, proposed_assignment)
        and existing_assignment.tenant_id == proposed_assignment.tenant_id
        and existing_assignment.overlaps(proposed_assignment)
        for existing_assignment in existing_assignments
    )


def validate_allocation_total(
    allocations: Iterable[PositionCostAllocation],
) -> Decimal:
    """Validate that allocation percentages total exactly 100%."""
    total = sum((allocation.percentage for allocation in allocations), Decimal("0"))
    if total != ALLOCATION_TOTAL_PERCENT:
        raise AllocationTotalError(
            f"Position cost allocation total must be exactly 100%, got {total}."
        )
    return total


def _same_assignee(first: PositionAssignment, second: PositionAssignment) -> bool:
    if first.employee_id is not None and second.employee_id is not None:
        return first.employee_id == second.employee_id
    if first.person_id is not None and second.person_id is not None:
        return first.person_id == second.person_id
    return False


def _date_range_contains(
    effective_from: date, effective_to: date | None, on_date: date
) -> bool:
    return effective_from <= on_date and (
        effective_to is None or on_date <= effective_to
    )


def _date_ranges_overlap(
    first_from: date,
    first_to: date | None,
    second_from: date,
    second_to: date | None,
) -> bool:
    first_end = first_to or date.max
    second_end = second_to or date.max
    return first_from <= second_end and second_from <= first_end
