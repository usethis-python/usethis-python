"""Container data structures for pipeline compositions."""

from __future__ import annotations

from pydantic import BaseModel, RootModel
from typing_extensions import override

_HASH_SALT = "e6fdde87-adc6-42f6-8e66-4aabe4ba05f2"


class Series(RootModel[list["Series | Parallel | DepGroup | str"]]):
    @override
    def __hash__(self):
        return hash((_HASH_SALT, tuple(self.root)))

    def __getitem__(self, item: int) -> Series | Parallel | DepGroup | str:
        return self.root[item]

    def __setitem__(self, item: int, value: Series | Parallel | DepGroup | str) -> None:
        self.root[item] = value

    @override
    def __eq__(self, other: object):
        if not isinstance(other, Series):
            return False
        return self.root == other.root

    def __len__(self):
        return len(self.root)


class Parallel(RootModel[frozenset["Series | Parallel | DepGroup | str"]]):
    @override
    def __hash__(self):
        return hash((_HASH_SALT, frozenset(self)))

    def __or__(self, other: Parallel) -> Parallel:
        return Parallel(self.root | other.root)

    @override
    def __eq__(self, other: object):
        if not isinstance(other, Parallel):
            return False

        if any(component not in list(self.root) for component in other.root):
            return False
        return not any(component not in list(other.root) for component in self.root)

    def __len__(self):
        return len(self.root)


class DepGroup(BaseModel):
    series: Series
    config_group: str

    @override
    def __hash__(self):
        return hash((_HASH_SALT, hash(self.series), self.config_group))


def parallel(*args: Series | Parallel | DepGroup | str) -> Parallel:
    """Create a Parallel container from the given components."""
    return Parallel(frozenset(args))


def series(*args: Series | Parallel | DepGroup | str) -> Series:
    """Create a Series container from the given components."""
    return Series(list(args))


def depgroup(*args: Series | Parallel | DepGroup | str, config_group: str) -> DepGroup:
    """Create a DepGroup container with the given components and configuration group."""
    return DepGroup(series=series(*args), config_group=config_group)
