# Authentication and Authorization

## Contract

IAM owns authentication, principals, roles, permissions, RBAC policies, and tenant scope. Business contexts consume a principal and check permissions through an auth port.

```python
class AuthProvider(Protocol):
    async def authenticate(self, username: str, password: str) -> Principal: ...
    def require_permission(self, principal: Principal, permission: str) -> None: ...
```

## Operational Boundary

- Prefer a self-hosted provider candidate first, with `fastapi-fullauth` evaluated before AuthFort.
- Keep the provider behind an adapter so Auth0/OIDC can be added later.
- Use RBAC as the default authorization model: users receive roles, roles receive permissions, and business contexts check permissions instead of hard-coding role names.
- Business contexts MUST NOT store passwords or provider session internals.
- Authorization failures are 403; authentication failures are 401.

## RBAC Rule

- IAM is the source of truth for roles and permissions.
- Context permissions SHOULD be named by bounded context and action, for example `crm.customer.read`, `crm.customer.write`, `sales.invoice.post`, and `accounting.journal-entry.read`.
- Controllers and services MUST check permissions through `AuthProvider.require_permission(...)` or an equivalent policy service.
