"""Explicit schema shapes for HR organizational structure services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from hr.domain.organization import VinculationType


@dataclass(frozen=True, slots=True)
class CreateOrganizationalUnitCommand:
    """Command to create an HR-owned organizational unit."""

    tenant_id: str
    unit_id: int
    name: str
    effective_from: date
    actor_id: str
    effective_to: date | None = None


@dataclass(frozen=True, slots=True)
class CreatePositionCommand:
    """Command to create a tenant-scoped HR position."""

    tenant_id: str
    position_id: int
    organizational_unit_id: int
    code: str
    title: str
    effective_from: date
    actor_id: str
    effective_to: date | None = None


@dataclass(frozen=True, slots=True)
class SetSuperiorPositionCommand:
    """Command to record an effective-dated position reporting line."""

    tenant_id: str
    position_id: int
    superior_position_id: int
    effective_from: date
    actor_id: str
    effective_to: date | None = None


@dataclass(frozen=True, slots=True)
class AssignPositionCommand:
    """Command to assign a person or employee to a position."""

    tenant_id: str
    position_id: int
    employee_id: int | None
    person_id: int | None
    contract_id: int
    effective_from: date
    actor_id: str
    effective_to: date | None = None
    vinculation_reference: str | None = None
    vinculation_type: VinculationType | None = None


@dataclass(frozen=True, slots=True)
class PositionCostAllocationInput:
    """Input item for setting a position cost-center allocation."""

    cost_center_id: int
    percentage: Decimal


@dataclass(frozen=True, slots=True)
class PositionCostAllocationCommand:
    """Command to replace effective-dated position cost-center allocations."""

    tenant_id: str
    position_id: int
    effective_from: date
    allocations: list[PositionCostAllocationInput]


@dataclass(frozen=True, slots=True)
class PositionCostAllocationRead:
    """Read model exposing Accounting cost-center code with HR allocation state."""

    position_id: int
    cost_center_id: int
    cost_center_code: str
    percentage: Decimal
    effective_from: date


@dataclass(frozen=True, slots=True)
class AuthorizationTargetRead:
    """Contract for future approval consumers resolving authorization positions."""

    requested_position_id: int
    resolved_position_id: int | None
    escalated_from_vacant_position: bool
