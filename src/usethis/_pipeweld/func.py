import contextlib
from functools import reduce, singledispatch
from typing import assert_never

from pydantic import BaseModel

from usethis._pipeweld.containers import Parallel, Series, parallel, series
from usethis._pipeweld.ops import InsertParallel
from usethis._pipeweld.result import WeldResult


def add(
    pipeline: Series,
    *,
    step: str,
    prerequisites: set[str] = set(),
    postrequisites: set[str] = set(),
) -> WeldResult:
    if len(pipeline) == 0:
        return WeldResult(
            instructions=[InsertParallel(before=None, step=step)],
            solution=series(step),
            traceback=[series(), series(step)],
        )

    instructions = []

    partitions = _get_series_partitions(
        pipeline,
        predecessor=None,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )

    step_partition = Partition(
        nondependent_component=step,
        top_ranked_endpoint=step,
    )

    inserted = False
    for idx, partition in reversed(list(enumerate(partitions))):
        # Find our final pre-requisite partition
        if partition.prerequisite_component is not None:
            # Insert the new step after the pre-requisite
            instructions.append(
                InsertParallel(before=partition.top_ranked_endpoint, step=step)
            )
            partitions[idx + 1] = _parallel_merge_partitions(
                partitions[idx + 1], step_partition
            )

            inserted = True
            break
    if not inserted:
        # No pre-requisites found, so insert at the start
        instructions.append(InsertParallel(before=None, step=step))
        partitions[0] = _parallel_merge_partitions(partitions[0], step_partition)

    solution_partition = reduce(_op_series_merge_partitions, partitions)

    solution = _flatten_partition(solution_partition)

    return WeldResult(
        instructions=instructions,
        solution=solution,
        traceback=[
            pipeline,
            solution,
        ],
    )


class Partition(BaseModel):
    prerequisite_component: str | Series | Parallel | None = None
    nondependent_component: str | Series | Parallel | None = None
    postrequisite_component: str | Series | Parallel | None = None
    top_ranked_endpoint: str


def _flatten_partition(partition: Partition) -> Series:
    return _concat(
        partition.prerequisite_component,
        partition.nondependent_component,
        partition.postrequisite_component,
    )


@singledispatch
def partition_component(
    component: str | Series | Parallel,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> Partition: ...


@partition_component.register(str)
def _(
    component: str,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> Partition:
    if component in prerequisites:
        return Partition(
            prerequisite_component=component,
            top_ranked_endpoint=component,
        )
    elif component in postrequisites:
        return Partition(
            postrequisite_component=component,
            top_ranked_endpoint=component,
        )
    else:
        return Partition(
            nondependent_component=component,
            top_ranked_endpoint=component,
        )


@partition_component.register(Parallel)
def _(
    component: Parallel,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> Partition:
    partitions = [
        partition_component(
            subcomponent,
            predecessor=predecessor,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )
        for subcomponent in component.root
    ]

    any_prerequisites = any(p.prerequisite_component is not None for p in partitions)
    any_postrequisites = any(p.postrequisite_component is not None for p in partitions)

    if any_prerequisites and any_postrequisites:
        return _parallel_merge_partitions(*partitions)
    elif any_prerequisites:
        return Partition(
            prerequisite_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        )
    elif any_postrequisites:
        return Partition(
            postrequisite_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        )
    else:
        return Partition(
            nondependent_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        )


@partition_component.register(Series)
def _(
    component: Series,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> Partition:
    partitions = _get_series_partitions(
        component,
        predecessor=predecessor,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )
    return reduce(_op_series_merge_partitions, partitions)


def _get_series_partitions(
    component: Series,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> list[Partition]:
    partitions: list[Partition] = []
    for subcomponent in component.root:
        partition = partition_component(
            subcomponent,
            predecessor=predecessor,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )
        partitions.append(partition)
        predecessor = partition.top_ranked_endpoint  # For the next iteration

    return partitions


def _op_series_merge_partitions(
    partition: Partition, next_partition: Partition
) -> Partition:
    if next_partition.prerequisite_component is not None:
        # TODO don't return; should be "accumulating" the binary operator
        # This is just applying it to the first two and returning
        # likely the pairwise generator is not the right choice.
        return Partition(
            prerequisite_component=_concat(
                partition.prerequisite_component,
                partition.nondependent_component,
                partition.postrequisite_component,
                next_partition.prerequisite_component,
            ),
            nondependent_component=next_partition.nondependent_component,
            postrequisite_component=next_partition.postrequisite_component,
            top_ranked_endpoint=next_partition.top_ranked_endpoint,
        )
    elif (
        next_partition.nondependent_component is not None
        and partition.postrequisite_component is not None
    ):
        return Partition(
            prerequisite_component=_concat(
                partition.prerequisite_component,
                next_partition.prerequisite_component,
            ),
            nondependent_component=partition.nondependent_component,
            postrequisite_component=_concat(
                partition.postrequisite_component,
                next_partition.nondependent_component,
                next_partition.postrequisite_component,
            ),
            top_ranked_endpoint=next_partition.top_ranked_endpoint,
        )
    else:
        return Partition(
            prerequisite_component=_concat(
                partition.prerequisite_component,
                next_partition.prerequisite_component,
            ),
            nondependent_component=_concat(
                partition.nondependent_component,
                next_partition.nondependent_component,
            ),
            postrequisite_component=_concat(
                partition.postrequisite_component,
                next_partition.postrequisite_component,
            ),
            top_ranked_endpoint=next_partition.top_ranked_endpoint,
        )


def _parallel_merge_partitions(*partitions: Partition) -> Partition:
    prerequisite_components = [
        p.prerequisite_component
        for p in partitions
        if p.prerequisite_component is not None
    ]
    nondependent_components = [
        p.nondependent_component
        for p in partitions
        if p.nondependent_component is not None
    ]
    postrequisite_components = [
        p.postrequisite_component
        for p in partitions
        if p.postrequisite_component is not None
    ]
    # Element-wise parallelism
    return Partition(
        prerequisite_component=_union(*prerequisite_components)
        if prerequisite_components
        else None,
        nondependent_component=_union(*nondependent_components)
        if nondependent_components
        else None,
        postrequisite_component=_union(*postrequisite_components)
        if postrequisite_components
        else None,
        top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
    )


def _concat(*components: str | Series | Parallel | None) -> Series:
    s = []
    for component in components:
        if isinstance(component, Series):
            s.extend(component.root)
        elif isinstance(component, Parallel | str):
            s.append(component)
        elif component is None:
            pass
        else:
            assert_never(component)
    return series(*s)


def _union(*components: str | Series | Parallel | None) -> Parallel:
    p = []
    for component in components:
        if isinstance(component, Parallel):
            p.extend(component.root)
        elif isinstance(component, Series | str):
            p.append(component)
        elif component is None:
            pass
        else:
            assert_never(component)
    return parallel(*p)


def get_endpoint(component: str | Series | Parallel) -> str:
    if isinstance(component, str):
        return component
    elif isinstance(component, Series):
        for subcomponent in reversed(component.root):
            try:
                return get_endpoint(subcomponent)
            except ValueError:
                pass

        msg = """No endpoints are defined for a Series with no steps"""
        raise ValueError(msg)
    elif isinstance(component, Parallel):
        endpoints = []
        for subcomponent in component.root:
            with contextlib.suppress(ValueError):
                endpoints.append(get_endpoint(subcomponent))
        # Any endpoint will do so choose the first one
        # alphabetically
        if not endpoints:
            msg = """No endpoints are defined for a Parallel block with no steps"""
            raise ValueError(msg)
        return sorted(endpoints)[0]
    else:
        assert_never(component)
