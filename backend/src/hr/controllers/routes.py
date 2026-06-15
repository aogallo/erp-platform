"""Route contract and empty FastAPI router for HR organization endpoints."""

from fastapi import APIRouter, HTTPException

ORGANIZATIONAL_UNITS_ROUTE_PREFIX = "/hr/organizational-units"
POSITIONS_ROUTE_PREFIX = "/hr/positions"
ORGANIZATIONAL_UNIT_SCAFFOLD_DETAIL = (
    "HR organizational unit endpoint scaffold is registered but not implemented."
)
POSITION_SCAFFOLD_DETAIL = (
    "HR position endpoint scaffold is registered but not implemented."
)

CREATE_ORGANIZATIONAL_UNIT_ROUTE = ORGANIZATIONAL_UNITS_ROUTE_PREFIX
LIST_ORGANIZATIONAL_UNITS_ROUTE = ORGANIZATIONAL_UNITS_ROUTE_PREFIX
CREATE_POSITION_ROUTE = POSITIONS_ROUTE_PREFIX
LIST_POSITIONS_ROUTE = POSITIONS_ROUTE_PREFIX
SET_POSITION_SUPERIOR_ROUTE = f"{POSITIONS_ROUTE_PREFIX}/{{position_id}}/superior"
ASSIGN_POSITION_ROUTE = f"{POSITIONS_ROUTE_PREFIX}/{{position_id}}/assignments"
SET_POSITION_COST_ALLOCATION_ROUTE = (
    f"{POSITIONS_ROUTE_PREFIX}/{{position_id}}/cost-allocations"
)

router = APIRouter(tags=["hr-organization"])


@router.get(ORGANIZATIONAL_UNITS_ROUTE_PREFIX)
async def list_organizational_units_scaffold() -> None:
    """Expose the HR organizational unit route while implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail=ORGANIZATIONAL_UNIT_SCAFFOLD_DETAIL,
    )


@router.get(POSITIONS_ROUTE_PREFIX)
async def list_positions_scaffold() -> None:
    """Expose the HR position route while implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail=POSITION_SCAFFOLD_DETAIL,
    )
