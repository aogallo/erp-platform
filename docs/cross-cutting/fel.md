# FEL Integration

## Contract

FEL is an outbound provider boundary for Guatemala electronic invoicing. The domain depends on a provider-neutral port, not Infile SDK/API details.

```python
class FelProvider(Protocol):
    async def authorize(self, invoice_id: int) -> FelResult: ...
    async def cancel_or_credit(self, invoice_id: int, reason: str) -> FelResult: ...
```

## Operational Boundary

- Local invoice posting commits inventory, accounting, and an outbox event first.
- FEL authorization runs asynchronously after commit.
- Provider outages MUST NOT roll back local posting.
- Transient failures SHOULD retry with backoff; exhausted attempts mark invoices for manual retry.
- Infile is the first adapter target, but domain language remains provider-neutral.
