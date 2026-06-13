"""Repository contracts for Accounting cost-center lookup boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol


class CostCenterValidationStatus(StrEnum):
    """Validation outcome for HR cost-center references."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    NOT_FOUND = "not_found"


@dataclass(frozen=True, slots=True)
class CostCenterValidationResult:
    """Accounting-owned cost-center reference exposed to HR."""

    cost_center_id: int
    status: CostCenterValidationStatus
    code: str | None = None
    name: str | None = None

    @property
    def is_active(self) -> bool:
        """Return whether the referenced cost center can be used by HR."""
        return self.status is CostCenterValidationStatus.ACTIVE


class AccountingCostCenterLookupPort(Protocol):
    """Read boundary for validating Accounting-owned cost centers from HR."""

    async def validate_active_cost_center(
        self, *, tenant_id: str, cost_center_id: int, effective_date: date
    ) -> CostCenterValidationResult:
        """Return active, inactive, or not-found status for a cost-center ID."""
