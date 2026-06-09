import inspect

from shared.uow import UnitOfWork


def test_unit_of_work_contract_exposes_transaction_methods() -> None:
    required_methods = {"__aenter__", "__aexit__", "commit", "rollback"}

    assert required_methods.issubset(set(UnitOfWork.__dict__))


def test_unit_of_work_commit_and_rollback_are_async() -> None:
    assert inspect.iscoroutinefunction(UnitOfWork.commit)
    assert inspect.iscoroutinefunction(UnitOfWork.rollback)
