import inspect
from typing import get_type_hints

from shared.uow import UnitOfWork


def test_unit_of_work_contract_exposes_transaction_methods() -> None:
    required_methods = {"__aenter__", "__aexit__", "commit", "rollback"}

    assert required_methods.issubset(set(UnitOfWork.__dict__))


def test_unit_of_work_commit_and_rollback_are_async() -> None:
    assert inspect.iscoroutinefunction(UnitOfWork.commit)
    assert inspect.iscoroutinefunction(UnitOfWork.rollback)


def test_unit_of_work_contract_exposes_hr_organization_ports() -> None:
    annotations = get_type_hints(UnitOfWork)

    assert annotations["hr_organization"].__name__ == "HROrganizationRepository"
    assert (
        annotations["accounting_cost_centers"].__name__
        == "AccountingCostCenterLookupPort"
    )
