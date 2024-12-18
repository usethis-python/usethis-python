from pydantic import BaseModel

from usethis._pipeweld.containers import Series
from usethis._pipeweld.ops import BaseOperation


class WeldResult(BaseModel):
    instructions: list[BaseOperation]
    solution: Series
    traceback: list[Series]
