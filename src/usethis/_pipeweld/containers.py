from pydantic import RootModel


class Series(RootModel[list["Series | Parallel | str"]]):
    def __hash__(self):
        return hash(tuple(self))

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return len(self.root)


class Parallel(RootModel[frozenset["Series | Parallel | str"]]):
    def __hash__(self):
        return hash(frozenset(self))


def parallel(*args: Series | Parallel | str) -> Parallel:
    return Parallel(frozenset(args))


def series(*args: Series | Parallel | str) -> Series:
    return Series(list(args))
