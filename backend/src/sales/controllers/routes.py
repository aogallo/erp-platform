"""Route contract and empty FastAPI router for Sales invoice endpoints."""

from fastapi import APIRouter, HTTPException

INVOICE_ROUTE_PREFIX = "/sales/invoices"

CREATE_INVOICE_ROUTE = INVOICE_ROUTE_PREFIX
QUERY_INVOICES_ROUTE = INVOICE_ROUTE_PREFIX
UPDATE_INVOICE_ROUTE = f"{INVOICE_ROUTE_PREFIX}/{{invoice_id}}"
DELETE_INVOICE_ROUTE = f"{INVOICE_ROUTE_PREFIX}/{{invoice_id}}"
POST_INVOICE_ROUTE = f"{INVOICE_ROUTE_PREFIX}/{{invoice_id}}/post"
CREDIT_NOTE_ROUTE = f"{INVOICE_ROUTE_PREFIX}/{{invoice_id}}/credit-note"
FEL_RETRY_ROUTE = f"{INVOICE_ROUTE_PREFIX}/{{invoice_id}}/fel-retry"

router = APIRouter(prefix=INVOICE_ROUTE_PREFIX, tags=["sales-invoices"])


@router.get("")
async def query_invoices_scaffold() -> None:
    """Expose the Sales invoice route while the feature implementation is pending."""
    raise HTTPException(
        status_code=501,
        detail="Sales invoice endpoint scaffold is registered but not implemented.",
    )
