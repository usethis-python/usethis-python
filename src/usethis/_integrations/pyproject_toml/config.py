from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from typing import Any


class PyprojectConfig(BaseModel):
    id_keys: list[str]
    value: Any
