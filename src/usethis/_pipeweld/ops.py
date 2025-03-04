from typing import TYPE_CHECKING, TypeAlias

from pydantic import BaseModel


class BaseOperation(BaseModel):
    after: str | None  # None represents the source node
    step: str


class InsertParallel(BaseOperation):
    pass


class InsertSuccessor(BaseOperation):
    pass


if TYPE_CHECKING:
    Instruction: TypeAlias = InsertSuccessor | InsertParallel
