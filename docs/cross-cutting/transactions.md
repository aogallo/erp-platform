# Transactions

## Contract

The transaction manager owns a single database transaction for an application use case. Services receive repositories through the transaction manager and call `commit()` only after all local changes and outbox messages are ready.

```python
class TransactionManager(Protocol):
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

## Operational Boundary

- Controllers MUST NOT open database transactions directly.
- Repositories MUST NOT commit independently.
- Cross-context local writes, such as invoice posting plus inventory and accounting updates, MUST run through one transaction manager.
- External provider calls MUST happen after commit through outbox-driven workers.

This interface applies the Unit of Work pattern while keeping the public code surface named around the business concept: transactions.
