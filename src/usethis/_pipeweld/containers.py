from pydantic import RootModel


class Series(RootModel[list["Series | Parallel | str"]]):
    def __hash__(self):
        return hash(tuple(self))

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, item, value):
        self.root[item] = value

    def __len__(self):
        return len(self.root)

    def __repr__(self):
        return str(self.root)

    def __print__(self):
        return str(self.root)


class Parallel(RootModel[frozenset["Series | Parallel | str"]]):
    def __hash__(self):
        return hash(frozenset(self))

    def __or__(self, other: "Parallel") -> "Parallel":
        return Parallel(self.root | other.root)

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
