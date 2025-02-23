from typing import Any

from pydantic import BaseModel


class PyprojectConfig(BaseModel):
    id_keys: list[str]
    value: Any
