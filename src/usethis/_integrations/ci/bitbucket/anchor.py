from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel
from ruamel.yaml.scalarstring import LiteralScalarString

ScriptItemName: TypeAlias = Literal["install-uv", "ensure-venv"]


class ScriptItemAnchor(BaseModel):
    name: ScriptItemName


def anchor_name_from_script_item(item: Any) -> str | None:
    """Extract the anchor name from a script item, if it has one."""
    if isinstance(item, LiteralScalarString):
        anchor = item.yaml_anchor()
        if anchor is not None:
            return anchor.value
    return None
