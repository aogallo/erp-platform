"""Shared pagination value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """Named paginated result.

    Prefer this over returning positional tuples like `(items, total)` so callers
    do not need to remember what each tuple position means.
    """

    items: tuple[T, ...]
    total: int
    page: int
    page_size: int
