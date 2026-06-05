"""Route contract for CRM customer endpoints.

FastAPI routers are intentionally not created in this PR because backend tooling
and dependencies are scheduled for a later scaffold slice. These constants keep
the route ownership explicit and import-safe with only the Python standard
library available.
"""

CUSTOMER_ROUTE_PREFIX = "/crm/customers"

CREATE_CUSTOMER_ROUTE = CUSTOMER_ROUTE_PREFIX
SEARCH_CUSTOMERS_ROUTE = CUSTOMER_ROUTE_PREFIX
UPDATE_CUSTOMER_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}"
DISABLE_CUSTOMER_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}"
ADD_CUSTOMER_CONTACT_ROUTE = f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}/contacts"
REMOVE_CUSTOMER_CONTACT_ROUTE = (
    f"{CUSTOMER_ROUTE_PREFIX}/{{customer_id}}/contacts/{{contact_id}}"
)
