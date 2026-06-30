from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import cast

import pytest

from accounting.repositories.contracts import (
    AccountingCostCenterLookupPort,
    CostCenterValidationResult,
    CostCenterValidationStatus,
)
from hr.domain.organization import (
    OrganizationalUnit,
    Position,
    PositionAssignment,
    PositionCostAllocation,
    PositionReportingLine,
    VinculationType,
)
from hr.repositories.contracts import HROrganizationRepository
from hr.schemas.organization import (
    AssignPositionCommand,
    CreateOrganizationalUnitCommand,
    CreatePositionCommand,
    PositionCostAllocationCommand,
    PositionCostAllocationInput,
    SetSuperiorPositionCommand,
)
from hr.services.organization import (
    ConcurrentPositionAssignmentError,
    CostCenterReferenceRejectedError,
    OrganizationApplicationService,
    OrganizationService,
    OrganizationUnitOfWork,
)


def assert_utc_audit(
    *,
    created_at: datetime | None,
    created_by: str | None,
    actor_id: str,
    before: datetime,
    after: datetime,
) -> None:
    assert created_by == actor_id
    assert created_at is not None
    assert created_at.tzinfo is UTC
    assert before <= created_at <= after


@dataclass(slots=True)
class FakeAccountingCostCenters:
    results: dict[int, CostCenterValidationResult]
    calls: list[tuple[str, int, date]] = field(
        default_factory=lambda: cast(list[tuple[str, int, date]], [])
    )

    async def validate_active_cost_center(
        self, *, tenant_id: str, cost_center_id: int, effective_date: date
    ) -> CostCenterValidationResult:
        self.calls.append((tenant_id, cost_center_id, effective_date))
        return self.results[cost_center_id]


@dataclass(slots=True)
class FakeHROrganizationRepository:
    position: Position
    units: list[OrganizationalUnit] = field(
        default_factory=lambda: cast(list[OrganizationalUnit], [])
    )
    positions: list[Position] = field(default_factory=lambda: cast(list[Position], []))
    active_assignments: list[PositionAssignment] = field(
        default_factory=lambda: cast(list[PositionAssignment], [])
    )
    reporting_lines: list[PositionReportingLine] = field(
        default_factory=lambda: cast(list[PositionReportingLine], [])
    )
    stored_allocations: list[PositionCostAllocation] = field(
        default_factory=lambda: cast(list[PositionCostAllocation], [])
    )
    replaced_allocations: int = 0
    approval_side_effects: int = 0

    async def get_position(
        self, *, tenant_id: str, position_id: int
    ) -> Position | None:
        if self.position.tenant_id == tenant_id and self.position.id == position_id:
            return self.position
        for position in self.positions:
            if position.tenant_id == tenant_id and position.id == position_id:
                return position
        return None

    async def add_organizational_unit(
        self, unit: OrganizationalUnit
    ) -> OrganizationalUnit:
        self.units.append(unit)
        return unit

    async def list_organizational_units(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[OrganizationalUnit]:
        return [
            unit
            for unit in self.units
            if unit.tenant_id == tenant_id
            and (effective_date is None or unit.is_effective_on(effective_date))
        ]

    async def get_organizational_unit(
        self, *, tenant_id: str, unit_id: int
    ) -> OrganizationalUnit | None:
        for unit in self.units:
            if unit.tenant_id == tenant_id and unit.id == unit_id:
                return unit
        return None

    async def add_position(self, position: Position) -> Position:
        self.positions.append(position)
        return position

    async def add_reporting_line(
        self, reporting_line: PositionReportingLine
    ) -> PositionReportingLine:
        self.reporting_lines.append(reporting_line)
        return reporting_line

    async def add_assignment(
        self, assignment: PositionAssignment
    ) -> PositionAssignment:
        self.active_assignments.append(assignment)
        return assignment

    async def list_active_assignments(
        self, *, tenant_id: str, employee_id: int | None, person_id: int | None
    ) -> list[PositionAssignment]:
        return [
            assignment
            for assignment in self.active_assignments
            if assignment.tenant_id == tenant_id
            and (
                (employee_id is not None and assignment.employee_id == employee_id)
                or (person_id is not None and assignment.person_id == person_id)
            )
        ]

    async def replace_cost_allocations(
        self, *, position_id: int, allocations: list[PositionCostAllocation]
    ) -> list[PositionCostAllocation]:
        self.replaced_allocations += 1
        self.stored_allocations = allocations
        return allocations

    async def list_reporting_lines(
        self, *, tenant_id: str, position_id: int
    ) -> list[PositionReportingLine]:
        return [
            line
            for line in self.reporting_lines
            if line.tenant_id == tenant_id and line.position_id == position_id
        ]


@dataclass(slots=True)
class FakeUnitOfWork:
    hr_organization: FakeHROrganizationRepository
    accounting_cost_centers: FakeAccountingCostCenters
    commits: int = 0

    async def commit(self) -> None:
        self.commits += 1


@pytest.mark.asyncio
async def test_create_organizational_unit_stamps_bounded_utc_audit_metadata() -> None:
    uow = FakeUnitOfWork(
        hr_organization=FakeHROrganizationRepository(
            position=Position(
                id=99,
                tenant_id="tenant-a",
                organizational_unit_id=20,
                code="P-99",
                title="Placeholder",
                effective_from=date(2026, 1, 1),
            )
        ),
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    before = datetime.now(UTC)
    created_unit = await service.create_organizational_unit(
        CreateOrganizationalUnitCommand(
            tenant_id="tenant-a",
            unit_id=21,
            name="Treasury",
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    after = datetime.now(UTC)

    assert_utc_audit(
        created_at=created_unit.created_at,
        created_by=created_unit.created_by,
        actor_id="user-10",
        before=before,
        after=after,
    )
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_create_position_stamps_bounded_utc_audit_metadata() -> None:
    uow = FakeUnitOfWork(
        hr_organization=FakeHROrganizationRepository(
            position=Position(
                id=99,
                tenant_id="tenant-a",
                organizational_unit_id=20,
                code="P-99",
                title="Placeholder",
                effective_from=date(2026, 1, 1),
            ),
            units=[
                OrganizationalUnit(
                    id=20,
                    tenant_id="tenant-a",
                    name="Finance",
                    effective_from=date(2026, 1, 1),
                )
            ],
        ),
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    before = datetime.now(UTC)
    created_position = await service.create_position(
        CreatePositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            organizational_unit_id=20,
            code="P-30",
            title="Treasury Analyst",
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    after = datetime.now(UTC)

    assert_utc_audit(
        created_at=created_position.created_at,
        created_by=created_position.created_by,
        actor_id="user-10",
        before=before,
        after=after,
    )
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_set_superior_position_stamps_bounded_utc_audit_metadata() -> None:
    uow = FakeUnitOfWork(
        hr_organization=FakeHROrganizationRepository(
            position=Position(
                id=30,
                tenant_id="tenant-a",
                organizational_unit_id=20,
                code="P-30",
                title="Treasury Analyst",
                effective_from=date(2026, 1, 1),
            ),
            positions=[
                Position(
                    id=99,
                    tenant_id="tenant-a",
                    organizational_unit_id=20,
                    code="P-99",
                    title="Finance Director",
                    effective_from=date(2026, 1, 1),
                )
            ],
        ),
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    before = datetime.now(UTC)
    reporting_line = await service.set_superior_position(
        SetSuperiorPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            superior_position_id=99,
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    after = datetime.now(UTC)

    assert_utc_audit(
        created_at=reporting_line.created_at,
        created_by=reporting_line.created_by,
        actor_id="user-10",
        before=before,
        after=after,
    )
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_assign_position_stamps_bounded_utc_audit_metadata() -> None:
    uow = FakeUnitOfWork(
        hr_organization=FakeHROrganizationRepository(
            position=Position(
                id=30,
                tenant_id="tenant-a",
                organizational_unit_id=20,
                code="P-30",
                title="Treasury Analyst",
                effective_from=date(2026, 1, 1),
            )
        ),
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    before = datetime.now(UTC)
    assignment = await service.assign_position(
        AssignPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            employee_id=100,
            person_id=None,
            contract_id=500,
            effective_from=date(2026, 3, 1),
            actor_id="user-10",
        )
    )
    after = datetime.now(UTC)

    assert_utc_audit(
        created_at=assignment.created_at,
        created_by=assignment.created_by,
        actor_id="user-10",
        before=before,
        after=after,
    )
    assert uow.hr_organization.active_assignments == [assignment]
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_set_position_cost_allocation_rejects_inactive_cost_center() -> None:
    position = Position(
        id=10,
        tenant_id="tenant-a",
        organizational_unit_id=20,
        code="P-10",
        title="Finance Manager",
        effective_from=date(2026, 1, 1),
    )
    uow = FakeUnitOfWork(
        hr_organization=FakeHROrganizationRepository(position=position),
        accounting_cost_centers=FakeAccountingCostCenters(
            results={
                3000: CostCenterValidationResult(
                    cost_center_id=3000,
                    status=CostCenterValidationStatus.INACTIVE,
                    code="CC-30",
                )
            }
        ),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    with pytest.raises(CostCenterReferenceRejectedError):
        await service.set_position_cost_allocation(
            PositionCostAllocationCommand(
                tenant_id="tenant-a",
                position_id=10,
                effective_from=date(2026, 4, 1),
                allocations=[
                    PositionCostAllocationInput(
                        cost_center_id=3000,
                        percentage=Decimal("100"),
                    )
                ],
            )
        )

    assert uow.accounting_cost_centers.calls == [
        ("tenant-a", 3000, date(2026, 4, 1))
    ]
    assert uow.hr_organization.replaced_allocations == 0
    assert uow.commits == 0


@pytest.mark.asyncio
async def test_set_position_cost_allocation_persists_split_and_returns_codes() -> None:
    position = Position(
        id=10,
        tenant_id="tenant-a",
        organizational_unit_id=20,
        code="P-10",
        title="Finance Manager",
        effective_from=date(2026, 1, 1),
    )
    repository = FakeHROrganizationRepository(position=position)
    cost_centers = FakeAccountingCostCenters(
        results={
            1000: CostCenterValidationResult(
                cost_center_id=1000,
                status=CostCenterValidationStatus.ACTIVE,
                code="CC-10",
            ),
            1001: CostCenterValidationResult(
                cost_center_id=1001,
                status=CostCenterValidationStatus.ACTIVE,
                code="CC-20",
            ),
        }
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=cost_centers,
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    read_model = await service.set_position_cost_allocation(
        PositionCostAllocationCommand(
            tenant_id="tenant-a",
            position_id=10,
            effective_from=date(2026, 4, 1),
            allocations=[
                PositionCostAllocationInput(
                    cost_center_id=1000,
                    percentage=Decimal("60"),
                ),
                PositionCostAllocationInput(
                    cost_center_id=1001,
                    percentage=Decimal("40"),
                ),
            ],
        )
    )

    assert cost_centers.calls == [
        ("tenant-a", 1000, date(2026, 4, 1)),
        ("tenant-a", 1001, date(2026, 4, 1)),
    ]
    stored_pairs = [
        (item.cost_center_id, item.percentage)
        for item in repository.stored_allocations
    ]
    assert stored_pairs == [
        (1000, Decimal("60")),
        (1001, Decimal("40")),
    ]
    assert [item.cost_center_code for item in read_model] == ["CC-10", "CC-20"]
    assert sum((item.percentage for item in read_model), Decimal("0")) == Decimal("100")
    assert repository.replaced_allocations == 1
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_vacant_position_escalates_without_workflow_side_effects() -> None:
    vacant_position = Position(
        id=10,
        tenant_id="tenant-a",
        organizational_unit_id=20,
        code="P-10",
        title="Finance Manager",
        effective_from=date(2026, 1, 1),
    )
    repository = FakeHROrganizationRepository(
        position=vacant_position,
        reporting_lines=[
            PositionReportingLine(
                tenant_id="tenant-a",
                position_id=10,
                superior_position_id=30,
                effective_from=date(2026, 2, 1),
            )
        ],
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    target = await service.resolve_authorization_target(
        tenant_id="tenant-a",
        position_id=10,
        on_date=date(2026, 2, 15),
    )

    assert target.requested_position_id == 10
    assert target.resolved_position_id == 30
    assert target.escalated_from_vacant_position is True
    assert repository.approval_side_effects == 0
    assert uow.commits == 0


@pytest.mark.asyncio
async def test_service_exposes_planned_organization_use_cases() -> None:
    service = OrganizationApplicationService(
        cast(
            OrganizationUnitOfWork,
            FakeUnitOfWork(
                hr_organization=FakeHROrganizationRepository(
                    position=Position(
                        id=99,
                        tenant_id="tenant-a",
                        organizational_unit_id=20,
                        code="P-99",
                        title="Placeholder",
                        effective_from=date(2026, 1, 1),
                    ),
                    units=[
                        OrganizationalUnit(
                            id=20,
                            tenant_id="tenant-a",
                            name="Finance",
                            effective_from=date(2026, 1, 1),
                        )
                    ],
                ),
                accounting_cost_centers=FakeAccountingCostCenters(results={}),
            ),
        )
    )
    assert isinstance(service, OrganizationService)

    created_unit = await service.create_organizational_unit(
        CreateOrganizationalUnitCommand(
            tenant_id="tenant-a",
            unit_id=21,
            name="Treasury",
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    units = await service.list_organizational_units(
        tenant_id="tenant-a", effective_date=date(2026, 2, 15)
    )
    created_position = await service.create_position(
        CreatePositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            organizational_unit_id=20,
            code="P-30",
            title="Treasury Analyst",
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    reporting_line = await service.set_superior_position(
        SetSuperiorPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            superior_position_id=99,
            effective_from=date(2026, 2, 1),
            actor_id="user-10",
        )
    )
    assignment = await service.assign_position(
        AssignPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            employee_id=100,
            person_id=None,
            contract_id=500,
            effective_from=date(2026, 3, 1),
            actor_id="user-10",
        )
    )

    assert created_unit.name == "Treasury"
    assert [unit.id for unit in units] == [20, 21]
    assert created_position.code == "P-30"
    assert reporting_line.superior_position_id == 99
    assert assignment.employee_id == 100


@pytest.mark.asyncio
async def test_create_position_rejects_cross_tenant_organizational_unit() -> None:
    repository = FakeHROrganizationRepository(
        position=Position(
            id=99,
            tenant_id="tenant-a",
            organizational_unit_id=20,
            code="P-99",
            title="Placeholder",
            effective_from=date(2026, 1, 1),
        ),
        units=[
            OrganizationalUnit(
                id=20,
                tenant_id="tenant-a",
                name="Finance",
                effective_from=date(2026, 1, 1),
            )
        ],
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    with pytest.raises(ValueError, match="Organizational unit"):
        await service.create_position(
            CreatePositionCommand(
                tenant_id="tenant-b",
                position_id=30,
                organizational_unit_id=20,
                code="P-30",
                title="Treasury Analyst",
                effective_from=date(2026, 2, 1),
                actor_id="user-20",
            )
        )

    assert repository.positions == []
    assert uow.commits == 0


@pytest.mark.asyncio
async def test_professional_services_label_is_not_decisive_for_vinculation() -> None:
    repository = FakeHROrganizationRepository(
        position=Position(
            id=30,
            tenant_id="tenant-a",
            organizational_unit_id=20,
            code="P-30",
            title="External Advisor",
            effective_from=date(2026, 1, 1),
        )
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    assignment = await service.assign_position(
        AssignPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            employee_id=None,
            person_id=200,
            contract_id=500,
            effective_from=date(2026, 3, 1),
            actor_id="user-10",
            vinculation_reference="professional services",
        )
    )

    assert assignment.vinculation_reference == "professional services"
    assert assignment.vinculation_type is None

    explicitly_classified = await service.assign_position(
        AssignPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            employee_id=None,
            person_id=201,
            contract_id=501,
            effective_from=date(2026, 3, 1),
            actor_id="user-10",
            vinculation_reference="external advisory agreement",
            vinculation_type=VinculationType.PROFESSIONAL_SERVICES,
        )
    )
    assert (
        explicitly_classified.vinculation_type
        is VinculationType.PROFESSIONAL_SERVICES
    )


@pytest.mark.asyncio
async def test_iam_linkage_remains_employee_reference_owned_by_hr_assignment() -> None:
    repository = FakeHROrganizationRepository(
        position=Position(
            id=30,
            tenant_id="tenant-a",
            organizational_unit_id=20,
            code="P-30",
            title="Treasury Analyst",
            effective_from=date(2026, 1, 1),
        )
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    assignment = await service.assign_position(
        AssignPositionCommand(
            tenant_id="tenant-a",
            position_id=30,
            employee_id=100,
            person_id=None,
            contract_id=500,
            effective_from=date(2026, 3, 1),
            actor_id="iam-user-10",
        )
    )

    assert assignment.employee_id == 100
    assert assignment.created_by == "iam-user-10"
    assert not hasattr(assignment, "iam_user_id")
    assert repository.active_assignments == [assignment]


@pytest.mark.asyncio
async def test_assign_position_rejects_concurrent_active_assignment() -> None:
    existing_assignment = PositionAssignment(
        tenant_id="tenant-a",
        position_id=40,
        employee_id=100,
        person_id=None,
        contract_id=499,
        effective_from=date(2026, 1, 1),
    )
    repository = FakeHROrganizationRepository(
        position=Position(
            id=30,
            tenant_id="tenant-a",
            organizational_unit_id=20,
            code="P-30",
            title="Treasury Analyst",
            effective_from=date(2026, 1, 1),
        ),
        active_assignments=[existing_assignment],
    )
    uow = FakeUnitOfWork(
        hr_organization=repository,
        accounting_cost_centers=FakeAccountingCostCenters(results={}),
    )
    service = OrganizationApplicationService(cast(OrganizationUnitOfWork, uow))

    with pytest.raises(ConcurrentPositionAssignmentError):
        await service.assign_position(
            AssignPositionCommand(
                tenant_id="tenant-a",
                position_id=30,
                employee_id=100,
                person_id=None,
                contract_id=500,
                effective_from=date(2026, 3, 1),
                actor_id="user-10",
            )
        )

    assert repository.active_assignments == [existing_assignment]
    assert uow.commits == 0


def test_accounting_cost_center_contract_is_lookup_only_for_hr() -> None:
    lifecycle_methods = {
        "create_cost_center",
        "activate_cost_center",
        "deactivate_cost_center",
    }

    assert hasattr(AccountingCostCenterLookupPort, "validate_active_cost_center")
    assert lifecycle_methods.isdisjoint(set(AccountingCostCenterLookupPort.__dict__))
    assert lifecycle_methods.isdisjoint(set(HROrganizationRepository.__dict__))
    assert lifecycle_methods.isdisjoint(set(OrganizationService.__dict__))
