import inspect
from typing import get_type_hints

from shared.transactions import TransactionManager


def test_transaction_manager_contract_exposes_transaction_methods() -> None:
    required_methods = {"__aenter__", "__aexit__", "commit", "rollback"}

    assert required_methods.issubset(set(TransactionManager.__dict__))


def test_transaction_manager_commit_and_rollback_are_async() -> None:
    assert inspect.iscoroutinefunction(TransactionManager.commit)
    assert inspect.iscoroutinefunction(TransactionManager.rollback)


def test_transaction_manager_contract_exposes_hr_organization_ports() -> None:
    annotations = get_type_hints(TransactionManager)

    assert annotations["hr_organization"].__name__ == "HROrganizationRepository"
    assert (
        annotations["accounting_cost_centers"].__name__
        == "AccountingCostCenterLookupPort"
    )
