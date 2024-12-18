from typing import assert_never

from usethis._pipeweld.containers import Parallel, Series, parallel, series
from usethis._pipeweld.ops import InsertParallel
from usethis._pipeweld.result import WeldResult


def add(pipeline: Series, *, step: str) -> WeldResult:
    if len(pipeline) > 0:
        # We're adding to a pipeline that already has elements so the way we add in
        # parallel will vary.
        component = pipeline.root[0]
        if isinstance(component, Parallel):
            solution = series(parallel(step) | component)
        elif isinstance(component, Series | str):
            solution = series(parallel(step, component))
        else:
            assert_never(component)
    else:
        solution = series(step)

    return WeldResult(
        instructions=[InsertParallel(before=None, step=step)],
        solution=solution,
        traceback=[
            pipeline,
            solution,
        ],
    )
