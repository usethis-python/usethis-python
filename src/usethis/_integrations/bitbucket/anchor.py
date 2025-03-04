from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel

# N.B. at the point where we support more than one script item, we should create a
# canonical sort order for them and enforce it when we add them to the pipeline.
ScriptItemName: TypeAlias = Literal["install-uv"]


class ScriptItemAnchor(BaseModel):
    name: ScriptItemName
