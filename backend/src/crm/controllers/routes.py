"""Route contract and empty FastAPI router for CRM customer endpoints."""

from fastapi import APIRouter, HTTPException

CUSTOMER_ROUTE_PREFIX = "/crm/customers"

CREATE_CUSTOMER_ROUTE = CUSTOMER_ROUTE_PREFIX
SEARCH_CUSTOMERS_ROUTE = CUSTOMER_ROUTE_PREFIX
UPDATE_CUSTOMER_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}"
DISABLE_CUSTOMER_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}"
ADD_CUSTOMER_CONTACT_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}/contacts"
REMOVE_CUSTOMER_CONTACT_ROUTE = (
    f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}/contacts/{{contact_id}}"
)

router = APIRouter(prefix=CUSTOMER_ROUTE_PREFIX, tags=["crm-customers"])


@router.get("")
async def search_customers_scaffold() -> None:
    """Expose the CRM customer route while the feature implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail="CRM customer endpoint scaffold is registered but not implemented.",
    )
