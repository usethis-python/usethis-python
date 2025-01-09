from typing import Literal

from pydantic import BaseModel

# N.B. at the point where we support more than one script item, we should create a
# canonical sort order for them and enforce it when we add them to the pipeline.
type ScriptItemName = Literal["install-uv"]


class ScriptItemAnchor(BaseModel):
    name: ScriptItemName
