from __future__ import annotations

from pydantic import BaseModel

from usethis._pipeweld.containers import Series
from usethis._pipeweld.ops import Instruction


class WeldResult(BaseModel):
    solution: Series
    instructions: list[Instruction]
