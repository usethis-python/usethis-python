from typing import Literal

from pydantic import BaseModel

type ScriptItemName = Literal["install-uv"]


class ScriptItemAnchor(BaseModel):
    name: ScriptItemName
