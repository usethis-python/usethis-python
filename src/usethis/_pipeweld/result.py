from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from usethis._pipeweld.containers import Series
    from usethis._pipeweld.ops import Instruction


class WeldResult(BaseModel):
    solution: Series
    instructions: list[Instruction]
