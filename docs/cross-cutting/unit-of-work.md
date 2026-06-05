# Unit of Work

## Contract

The Unit of Work owns a single database transaction for an application use case. Services receive repositories through the Unit of Work and call `commit()` only after all local changes and outbox messages are ready.

```python
class UnitOfWork(Protocol):
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

## Operational Boundary

- Controllers MUST NOT open database transactions directly.
- Repositories MUST NOT commit independently.
- Cross-context local writes, such as invoice posting plus inventory and accounting updates, MUST run in one Unit of Work.
- External provider calls MUST happen after commit through outbox-driven workers.
