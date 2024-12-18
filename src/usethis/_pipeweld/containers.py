from pydantic import RootModel


class Series(RootModel[list["Series | Parallel | str"]]):
    def __hash__(self):
        return hash(tuple(self))


class Parallel(RootModel[frozenset["Series | Parallel | str"]]):
    pass
