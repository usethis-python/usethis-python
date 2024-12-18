from usethis._pipeweld.containers import Series, parallel, series
from usethis._pipeweld.ops import InsertParallel
from usethis._pipeweld.result import WeldResult


def add(pipeline: Series, *, step: str) -> WeldResult:
    if len(pipeline) > 0:
        solution = series(parallel(step, pipeline.root[0]))
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
