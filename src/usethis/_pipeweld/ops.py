"""Operation and instruction types for pipeline welding."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel


class BaseOperation(BaseModel):
    """Base class for pipeline insertion operations."""

    after: str | None  # None represents the source node
    step: str


class InsertParallel(BaseOperation):
    """Insert a step in parallel with the step after the given predecessor."""

    pass


class InsertSuccessor(BaseOperation):
    """Insert a step as the immediate successor of the given predecessor."""

    pass


Instruction: TypeAlias = InsertSuccessor | InsertParallel
