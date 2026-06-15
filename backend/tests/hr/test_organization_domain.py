from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

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


def test_position_without_employee_is_valid_vacant_authorization_position() -> None:
    unit = OrganizationalUnit(
        id=10,
        tenant_id="tenant-a",
        name="Finance",
        effective_from=date(2026, 1, 1),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        created_by="user-10",
    )

    position = Position(
        id=20,
        tenant_id="tenant-a",
        organizational_unit_id=unit.id,
        code="P-10",
        title="Finance Manager",
        effective_from=date(2026, 1, 1),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        created_by="user-10",
    )

    assert position.is_vacant is True
    assert position.assigned_employee_id is None


def test_effective_dated_superior_lookup_returns_matching_line() -> None:
    reporting_lines = [
        PositionReportingLine(
            tenant_id="tenant-a",
            position_id=10,
            superior_position_id=20,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 1, 31),
        ),
        PositionReportingLine(
            tenant_id="tenant-a",
            position_id=10,
            superior_position_id=30,
            effective_from=date(2026, 2, 1),
        ),
    ]

    assert (
        find_effective_superior_position_id(
            reporting_lines,
            tenant_id="tenant-a",
            position_id=10,
            on_date=date(2026, 2, 15),
        )
        == 30
    )
    assert (
        find_effective_superior_position_id(
            reporting_lines,
            tenant_id="tenant-a",
            position_id=10,
            on_date=date(2026, 1, 15),
        )
        == 20
    )


def test_overlapping_active_assignment_detects_concurrent_employee_assignment() -> None:
    existing_assignment = PositionAssignment(
        tenant_id="tenant-a",
        position_id=10,
        employee_id=100,
        person_id=None,
        contract_id=500,
        effective_from=date(2026, 3, 1),
    )
    proposed_assignment = PositionAssignment(
        tenant_id="tenant-a",
        position_id=20,
        employee_id=100,
        person_id=None,
        contract_id=501,
        effective_from=date(2026, 3, 15),
    )
    later_assignment = PositionAssignment(
        tenant_id="tenant-a",
        position_id=30,
        employee_id=100,
        person_id=None,
        contract_id=502,
        effective_from=date(2026, 4, 1),
        effective_to=date(2026, 4, 30),
    )

    assert (
        has_overlapping_assignment([existing_assignment], proposed_assignment) is True
    )
    assert has_overlapping_assignment([later_assignment], proposed_assignment) is True
    assert (
        has_overlapping_assignment(
            [
                PositionAssignment(
                    tenant_id="tenant-a",
                    position_id=40,
                    employee_id=100,
                    person_id=None,
                    contract_id=503,
                    effective_from=date(2026, 1, 1),
                    effective_to=date(2026, 2, 28),
                )
            ],
            proposed_assignment,
        )
        is False
    )


def test_decimal_allocation_total_must_equal_exactly_100_percent() -> None:
    valid_allocations = [
        PositionCostAllocation(
            tenant_id="tenant-a",
            position_id=10,
            cost_center_id=1000,
            percentage=Decimal("60"),
            effective_from=date(2026, 4, 1),
        ),
        PositionCostAllocation(
            tenant_id="tenant-a",
            position_id=10,
            cost_center_id=1001,
            percentage=Decimal("40"),
            effective_from=date(2026, 4, 1),
        ),
    ]

    assert validate_allocation_total(valid_allocations) == Decimal("100")

    invalid_allocations = [
        PositionCostAllocation(
            tenant_id="tenant-a",
            position_id=10,
            cost_center_id=1000,
            percentage=Decimal("33.33"),
            effective_from=date(2026, 4, 1),
        ),
        PositionCostAllocation(
            tenant_id="tenant-a",
            position_id=10,
            cost_center_id=1001,
            percentage=Decimal("66.66"),
            effective_from=date(2026, 4, 1),
        ),
    ]
    with pytest.raises(AllocationTotalError):
        validate_allocation_total(invalid_allocations)
