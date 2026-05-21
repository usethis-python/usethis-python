"""Type aliases for Pydantic model representations."""

from types import NoneType
from typing import TypeAlias

from pydantic import BaseModel

ModelLiteral: TypeAlias = bool | int | float | str | NoneType
ModelRepresentation: TypeAlias = (
    ModelLiteral
    | dict[str, "ModelRepresentation"]
    | list["ModelRepresentation"]
    | BaseModel
)
