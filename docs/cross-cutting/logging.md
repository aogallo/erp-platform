# Logging

## Contract

Use structured logs with correlation IDs, tenant IDs when available, context name, use-case name, and safe business identifiers.

Required fields:

- `correlation_id`
- `tenant_id`
- `context`
- `use_case`
- `event`

## Operational Boundary

- Do not log passwords, tokens, provider secrets, full request bodies, or payment credentials.
- Log external provider calls at the adapter boundary with request IDs and sanitized status.
- Business services log decisions; repositories log technical failures only when useful for diagnosis.
