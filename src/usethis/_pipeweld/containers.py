from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from typing import Any


_HASH_SALT = "e6fdde87-adc6-42f6-8e66-4aabe4ba05f2"


class Series(RootModel[list["Series | Parallel | DepGroup | str"]]):
    def __hash__(self):
        return hash((_HASH_SALT, tuple(self.root)))

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, item, value):
        self.root[item] = value

    def __eq__(self, other: Any):
        if not isinstance(other, Series):
            return False
        return self.root == other.root

    def __len__(self):
        return len(self.root)


class Parallel(RootModel[frozenset["Series | Parallel | DepGroup | str"]]):
    def __hash__(self):
        return hash((_HASH_SALT, frozenset(self)))

    def __or__(self, other: Parallel) -> Parallel:
        return Parallel(self.root | other.root)

    def __eq__(self, other: Any):
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

    def __hash__(self):
        return hash((_HASH_SALT, hash(self.series), self.config_group))


def parallel(*args: Series | Parallel | DepGroup | str) -> Parallel:
    return Parallel(frozenset(args))


def series(*args: Series | Parallel | DepGroup | str) -> Series:
    return Series(list(args))


def depgroup(*args: Series | Parallel | DepGroup | str, config_group: str) -> DepGroup:
    return DepGroup(series=series(*args), config_group=config_group)
