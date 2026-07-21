"""Compatibility exports for transaction-manager contracts."""

from shared.transactions.ports import (
    AccountingCoordinationPort,
    CustomerLookupPort,
    InventoryCoordinationPort,
    TransactionManager,
)

__all__ = [
    "AccountingCoordinationPort",
    "CustomerLookupPort",
    "InventoryCoordinationPort",
    "TransactionManager",
]
