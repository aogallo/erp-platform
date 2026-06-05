# Error Handling

## Contract

Application services raise typed application errors. Controllers translate them to stable HTTP responses.

| Error | HTTP Status | Use |
|-------|-------------|-----|
| ValidationError | 422 | Invalid command shape or immutable field changes. |
| NotFoundError | 404 | Missing aggregate or referenced entity. |
| ConflictError | 409 | Duplicate tax ID, disabled customer, immutable invoice, or business conflict. |
| UnauthorizedError | 401 | Missing or invalid principal. |
| ForbiddenError | 403 | Principal lacks permission. |

## Operational Boundary

- Domain errors SHOULD be explicit and meaningful.
- Provider errors MUST be wrapped before crossing into application services.
- API responses MUST avoid leaking stack traces, SQL details, secrets, or provider payloads.
