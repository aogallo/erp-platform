"""HR organizational structure domain model."""

from hr.domain.organization import (
    AllocationTotalError,
    OrganizationalUnit,
    Position,
    PositionAssignment,
    PositionCostAllocation,
    PositionReportingLine,
    find_effective_superior_position_id,
    has_overlapping_assignment,
    validate_allocation_total,
)

__all__ = [
    "AllocationTotalError",
    "OrganizationalUnit",
    "Position",
    "PositionAssignment",
    "PositionCostAllocation",
    "PositionReportingLine",
    "find_effective_superior_position_id",
    "has_overlapping_assignment",
    "validate_allocation_total",
]
