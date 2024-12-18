from typing import assert_never

from usethis._pipeweld.containers import Parallel, Series, parallel, series
from usethis._pipeweld.ops import InsertParallel
from usethis._pipeweld.result import WeldResult


def add(pipeline: Series, *, step: str) -> WeldResult:
    if len(pipeline) == 0:
        return WeldResult(
            instructions=[InsertParallel(before=None, step=step)],
            solution=series(step),
            traceback=[series(), series(step)],
        )

    solution = pipeline.model_copy(deep=True)
    if isinstance(pipeline[0], Parallel):
        solution[0] = parallel(step) | pipeline[0]
    elif isinstance(pipeline[0], Series | str):
        solution[0] = parallel(step, pipeline[0])
    else:
        assert_never(pipeline[0])

    return WeldResult(
        instructions=[InsertParallel(before=None, step=step)],
        solution=solution,
        traceback=[
            pipeline,
            solution,
        ],
    )
