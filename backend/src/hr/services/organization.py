"""Application services for HR organizational structure rules."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Protocol, runtime_checkable

from accounting.repositories.contracts import CostCenterValidationResult
from hr.domain.organization import (
    OrganizationalUnit,
    Position,
    PositionAssignment,
    PositionCostAllocation,
    PositionReportingLine,
    find_effective_superior_position_id,
    has_overlapping_assignment,
    validate_allocation_total,
)
from hr.schemas.organization import (
    AssignPositionCommand,
    AuthorizationTargetRead,
    CreateOrganizationalUnitCommand,
    CreatePositionCommand,
    PositionCostAllocationCommand,
    PositionCostAllocationRead,
    SetSuperiorPositionCommand,
)


class CostCenterReferenceRejectedError(ValueError):
    """Raised when Accounting rejects a cost-center reference for HR allocation."""


class ConcurrentPositionAssignmentError(ValueError):
    """Raised when a person or employee already has an active position assignment."""


@runtime_checkable
class OrganizationService(Protocol):
    """Contract for HR organizational structure use cases."""

    async def create_organizational_unit(
        self, command: CreateOrganizationalUnitCommand
    ) -> OrganizationalUnit:
        """Create a tenant-scoped organizational unit."""

    async def list_organizational_units(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[OrganizationalUnit]:
        """List tenant-scoped organizational units."""

    async def create_position(self, command: CreatePositionCommand) -> Position:
        """Create a tenant-scoped position under an existing unit."""

    async def set_superior_position(
        self, command: SetSuperiorPositionCommand
    ) -> PositionReportingLine:
        """Record the superior position/reporting line for a position."""

    async def assign_position(
        self, command: AssignPositionCommand
    ) -> PositionAssignment:
        """Assign a person or employee to a position."""

    async def set_position_cost_allocation(
        self, command: PositionCostAllocationCommand
    ) -> list[PositionCostAllocationRead]:
        """Validate and replace position cost-center allocations."""

    async def validate_authorization_target(
        self, *, tenant_id: str, position_id: int, on_date: date
    ) -> AuthorizationTargetRead:
        """Validate the authorization target for future approval consumers."""


class OrganizationRepositoryPort(Protocol):
    """Repository behavior required by the organization application service."""

    async def get_position(
        self, *, tenant_id: str, position_id: int
    ) -> Position | None:
        """Return a tenant-scoped position by ID."""

    async def add_organizational_unit(
        self, unit: OrganizationalUnit
    ) -> OrganizationalUnit:
        """Persist an organizational unit."""

    async def get_organizational_unit(
        self, *, tenant_id: str, unit_id: int
    ) -> OrganizationalUnit | None:
        """Return a tenant-scoped organizational unit by ID."""

    async def list_organizational_units(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[OrganizationalUnit]:
        """Return tenant-scoped organizational units."""

    async def add_position(self, position: Position) -> Position:
        """Persist a position."""

    async def add_reporting_line(
        self, reporting_line: PositionReportingLine
    ) -> PositionReportingLine:
        """Persist a position reporting line."""

    async def add_assignment(
        self, assignment: PositionAssignment
    ) -> PositionAssignment:
        """Persist a position assignment."""

    async def list_active_assignments(
        self, *, tenant_id: str, employee_id: int | None, person_id: int | None
    ) -> list[PositionAssignment]:
        """Return active assignments for the assignee."""

    async def replace_cost_allocations(
        self, *, position_id: int, allocations: list[PositionCostAllocation]
    ) -> list[PositionCostAllocation]:
        """Replace cost-center allocations for a position."""

    async def list_reporting_lines(
        self, *, tenant_id: str, position_id: int
    ) -> list[PositionReportingLine]:
        """Return tenant-scoped reporting lines for a position."""


class AccountingCostCenterPort(Protocol):
    """Accounting boundary used by HR for cost-center validation."""

    async def validate_active_cost_center(
        self, *, tenant_id: str, cost_center_id: int, effective_date: date
    ) -> CostCenterValidationResult:
        """Return Accounting's validation result for a cost-center ID."""


class OrganizationUnitOfWork(Protocol):
    """Unit of Work subset used by HR organization services."""

    @property
    def hr_organization(self) -> OrganizationRepositoryPort:
        """Return the HR organization repository port."""

    @property
    def accounting_cost_centers(self) -> AccountingCostCenterPort:
        """Return the Accounting cost-center lookup port."""

    async def commit(self) -> None:
        """Commit the local transaction."""


class OrganizationApplicationService:
    """Application service coordinating HR rules and cross-context boundaries."""

    def __init__(self, uow: OrganizationUnitOfWork) -> None:
        self._uow = uow

    async def create_organizational_unit(
        self, command: CreateOrganizationalUnitCommand
    ) -> OrganizationalUnit:
        """Create a tenant-scoped organizational unit with audit metadata."""
        unit = OrganizationalUnit(
            id=command.unit_id,
            tenant_id=command.tenant_id,
            name=command.name,
            effective_from=command.effective_from,
            effective_to=command.effective_to,
            created_at=_utc_now(),
            created_by=command.actor_id,
        )
        stored_unit = await self._uow.hr_organization.add_organizational_unit(unit)
        await self._uow.commit()
        return stored_unit

    async def list_organizational_units(
        self, *, tenant_id: str, effective_date: date | None = None
    ) -> list[OrganizationalUnit]:
        """List tenant-scoped organizational units through the repository boundary."""
        return await self._uow.hr_organization.list_organizational_units(
            tenant_id=tenant_id, effective_date=effective_date
        )

    async def create_position(self, command: CreatePositionCommand) -> Position:
        """Create a vacant position under an existing tenant-scoped unit."""
        unit = await self._uow.hr_organization.get_organizational_unit(
            tenant_id=command.tenant_id, unit_id=command.organizational_unit_id
        )
        if unit is None:
            raise ValueError("Organizational unit was not found for the tenant.")

        position = Position(
            id=command.position_id,
            tenant_id=command.tenant_id,
            organizational_unit_id=command.organizational_unit_id,
            code=command.code,
            title=command.title,
            effective_from=command.effective_from,
            effective_to=command.effective_to,
            created_at=_utc_now(),
            created_by=command.actor_id,
        )
        stored_position = await self._uow.hr_organization.add_position(position)
        await self._uow.commit()
        return stored_position

    async def set_superior_position(
        self, command: SetSuperiorPositionCommand
    ) -> PositionReportingLine:
        """Record an effective-dated reporting line between tenant-scoped positions."""
        position = await self._uow.hr_organization.get_position(
            tenant_id=command.tenant_id, position_id=command.position_id
        )
        superior_position = await self._uow.hr_organization.get_position(
            tenant_id=command.tenant_id, position_id=command.superior_position_id
        )
        if position is None or superior_position is None:
            raise ValueError(
                "Position or superior position was not found for the tenant."
            )

        reporting_line = PositionReportingLine(
            tenant_id=command.tenant_id,
            position_id=command.position_id,
            superior_position_id=command.superior_position_id,
            effective_from=command.effective_from,
            effective_to=command.effective_to,
            created_at=_utc_now(),
            created_by=command.actor_id,
        )
        stored_line = await self._uow.hr_organization.add_reporting_line(
            reporting_line
        )
        await self._uow.commit()
        return stored_line

    async def assign_position(
        self, command: AssignPositionCommand
    ) -> PositionAssignment:
        """Assign a person or employee while enforcing one active assignment."""
        if command.employee_id is None and command.person_id is None:
            raise ValueError("A position assignment requires an employee or person ID.")

        position = await self._uow.hr_organization.get_position(
            tenant_id=command.tenant_id, position_id=command.position_id
        )
        if position is None:
            raise ValueError("Position was not found for the tenant.")

        proposed_assignment = PositionAssignment(
            tenant_id=command.tenant_id,
            position_id=command.position_id,
            employee_id=command.employee_id,
            person_id=command.person_id,
            contract_id=command.contract_id,
            effective_from=command.effective_from,
            effective_to=command.effective_to,
            vinculation_type=command.vinculation_type,
            vinculation_reference=command.vinculation_reference,
            created_at=_utc_now(),
            created_by=command.actor_id,
        )
        active_assignments = await self._uow.hr_organization.list_active_assignments(
            tenant_id=command.tenant_id,
            employee_id=command.employee_id,
            person_id=command.person_id,
        )
        if has_overlapping_assignment(active_assignments, proposed_assignment):
            raise ConcurrentPositionAssignmentError(
                "A person or employee can have only one active position assignment."
            )

        stored_assignment = await self._uow.hr_organization.add_assignment(
            proposed_assignment
        )
        await self._uow.commit()
        return stored_assignment

    async def set_position_cost_allocation(
        self, command: PositionCostAllocationCommand
    ) -> list[PositionCostAllocationRead]:
        """Validate cost centers through Accounting and store HR allocation IDs."""
        position = await self._uow.hr_organization.get_position(
            tenant_id=command.tenant_id, position_id=command.position_id
        )
        if position is None:
            raise ValueError("Position was not found for the tenant.")

        validation_results: list[CostCenterValidationResult] = []
        for allocation in command.allocations:
            validation = (
                await self._uow.accounting_cost_centers.validate_active_cost_center(
                    tenant_id=command.tenant_id,
                    cost_center_id=allocation.cost_center_id,
                    effective_date=command.effective_from,
                )
            )
            if not validation.is_active or validation.code is None:
                raise CostCenterReferenceRejectedError(
                    "Cost center "
                    f"{allocation.cost_center_id} is not active for HR allocation."
                )
            validation_results.append(validation)

        allocations = [
            PositionCostAllocation(
                tenant_id=command.tenant_id,
                position_id=command.position_id,
                cost_center_id=allocation.cost_center_id,
                percentage=allocation.percentage,
                effective_from=command.effective_from,
                cost_center_code=validation.code,
            )
            for allocation, validation in zip(
                command.allocations, validation_results, strict=True
            )
        ]
        validate_allocation_total(allocations)

        stored_allocations = await self._uow.hr_organization.replace_cost_allocations(
            position_id=command.position_id, allocations=allocations
        )
        await self._uow.commit()

        return [
            PositionCostAllocationRead(
                position_id=allocation.position_id,
                cost_center_id=allocation.cost_center_id,
                cost_center_code=allocation.cost_center_code or "",
                percentage=allocation.percentage,
                effective_from=allocation.effective_from,
            )
            for allocation in stored_allocations
        ]

    async def validate_authorization_target(
        self, *, tenant_id: str, position_id: int, on_date: date
    ) -> AuthorizationTargetRead:
        """Resolve vacancy escalation data without creating workflow side effects."""
        position = await self._uow.hr_organization.get_position(
            tenant_id=tenant_id, position_id=position_id
        )
        if position is None:
            raise ValueError("Position was not found for the tenant.")

        if not position.is_vacant:
            return AuthorizationTargetRead(
                requested_position_id=position_id,
                resolved_position_id=position_id,
                escalated_from_vacant_position=False,
            )

        reporting_lines = await self._uow.hr_organization.list_reporting_lines(
            tenant_id=tenant_id, position_id=position_id
        )
        superior_position_id = find_effective_superior_position_id(
            reporting_lines,
            tenant_id=tenant_id,
            position_id=position_id,
            on_date=on_date,
        )
        return AuthorizationTargetRead(
            requested_position_id=position_id,
            resolved_position_id=superior_position_id,
            escalated_from_vacant_position=superior_position_id is not None,
        )

    async def resolve_authorization_target(
        self, *, tenant_id: str, position_id: int, on_date: date
    ) -> AuthorizationTargetRead:
        """Backward-compatible alias for authorization-target validation."""
        return await self.validate_authorization_target(
            tenant_id=tenant_id, position_id=position_id, on_date=on_date
        )


def _utc_now() -> datetime:
    return datetime.now(UTC)
