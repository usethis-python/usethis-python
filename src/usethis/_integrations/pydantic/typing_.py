"""Type aliases for Pydantic model representations."""

from typing import TypeAlias

from pydantic import BaseModel

ModelLiteral: TypeAlias = bool | int | float | str
ModelRepresentation: TypeAlias = (
    ModelLiteral
    | dict[str, "ModelRepresentation"]
    | list["ModelRepresentation"]
    | BaseModel
)
