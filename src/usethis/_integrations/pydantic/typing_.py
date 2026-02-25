from typing import TypeAlias

from pydantic import BaseModel

from usethis._file.yaml.typing_ import YAMLLiteral

ModelLiteral: TypeAlias = bool | int | float | str
ModelRepresentation: TypeAlias = (
    ModelLiteral
    | dict[str, "ModelRepresentation"]
    | list["ModelRepresentation"]
    | BaseModel
    | YAMLLiteral
)
