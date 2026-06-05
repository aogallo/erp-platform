# Authentication and Authorization

## Contract

IAM owns authentication, principals, roles, permissions, and tenant scope. Business contexts consume a principal and check permissions through an auth port.

```python
class AuthProvider(Protocol):
    async def authenticate(self, username: str, password: str) -> Principal: ...
    def require_permission(self, principal: Principal, permission: str) -> None: ...
```

## Operational Boundary

- Prefer a self-hosted provider candidate first, with `fastapi-fullauth` evaluated before AuthFort.
- Keep the provider behind an adapter so Auth0/OIDC can be added later.
- Business contexts MUST NOT store passwords or provider session internals.
- Authorization failures are 403; authentication failures are 401.
