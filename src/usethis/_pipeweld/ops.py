from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel


class BaseOperation(BaseModel):
    after: str | None  # None represents the source node
    step: str


class InsertParallel(BaseOperation):
    pass


class InsertSuccessor(BaseOperation):
    pass


Instruction: TypeAlias = InsertSuccessor | InsertParallel
