from usethis._pipeweld.containers import Series
from usethis._pipeweld.ops import InsertSeries
from usethis._pipeweld.result import WeldResult


def add(pipeline: Series, *, step: str) -> WeldResult:
    return WeldResult(
        instructions=[InsertSeries(before=None, step=step)],
        solution=Series([step]),
        traceback=[pipeline, Series([step])],
    )
