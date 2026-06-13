"""Route contract and empty FastAPI router for HR organization endpoints."""

from fastapi import APIRouter, HTTPException

ORGANIZATIONAL_UNITS_ROUTE_PREFIX = "/hr/organizational-units"
PLAZAS_ROUTE_PREFIX = "/hr/plazas"
ORGANIZATIONAL_UNIT_SCAFFOLD_DETAIL = (
    "HR organizational unit endpoint scaffold is registered but not implemented."
)
PLAZA_SCAFFOLD_DETAIL = "HR plaza endpoint scaffold is registered but not implemented."

CREATE_ORGANIZATIONAL_UNIT_ROUTE = ORGANIZATIONAL_UNITS_ROUTE_PREFIX
LIST_ORGANIZATIONAL_UNITS_ROUTE = ORGANIZATIONAL_UNITS_ROUTE_PREFIX
CREATE_PLAZA_ROUTE = PLAZAS_ROUTE_PREFIX
LIST_PLAZAS_ROUTE = PLAZAS_ROUTE_PREFIX
SET_PLAZA_SUPERIOR_ROUTE = f"{PLAZAS_ROUTE_PREFIX}/{{plaza_id}}/superior"
ASSIGN_PLAZA_ROUTE = f"{PLAZAS_ROUTE_PREFIX}/{{plaza_id}}/assignments"
SET_PLAZA_COST_ALLOCATION_ROUTE = f"{PLAZAS_ROUTE_PREFIX}/{{plaza_id}}/cost-allocations"

router = APIRouter(tags=["hr-organization"])


@router.get(ORGANIZATIONAL_UNITS_ROUTE_PREFIX)
async def list_organizational_units_scaffold() -> None:
    """Expose the HR organizational unit route while implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail=ORGANIZATIONAL_UNIT_SCAFFOLD_DETAIL,
    )


@router.get(PLAZAS_ROUTE_PREFIX)
async def list_plazas_scaffold() -> None:
    """Expose the HR plaza route while implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail=PLAZA_SCAFFOLD_DETAIL,
    )
