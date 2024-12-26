from typing import Any

from pydantic import RootModel

_HASH_SALT = "e6fdde87-adc6-42f6-8e66-4aabe4ba05f2"


class Series(RootModel[list["Series | Parallel | str"]]):
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

    def __repr__(self):
        return str(self.root)

    def __print__(self):
        return str(self.root)


class Parallel(RootModel[frozenset["Series | Parallel | str"]]):
    def __hash__(self):
        return hash((_HASH_SALT, frozenset(self)))

    def __or__(self, other: "Parallel") -> "Parallel":
        return Parallel(self.root | other.root)

    def __eq__(self, other: Any):
        if not isinstance(other, Parallel):
            return False

        if any(component not in list(self.root) for component in other.root):
            return False
        return not any(component not in list(other.root) for component in self.root)

    def __len__(self):
        return len(self.root)

    def __repr__(self):
        return str(set(self.root))

    def __print__(self):
        return str(set(self.root))


def parallel(*args: Series | Parallel | str) -> Parallel:
    return Parallel(frozenset(args))


def series(*args: Series | Parallel | str) -> Series:
    return Series(list(args))
