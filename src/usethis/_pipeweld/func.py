import contextlib
from functools import reduce, singledispatch
from typing import assert_never

from pydantic import BaseModel

from usethis._pipeweld.containers import (
    DepGroup,
    Parallel,
    Series,
    depgroup,
    parallel,
    series,
)
from usethis._pipeweld.ops import BaseOperation, InsertParallel, InsertSuccessor
from usethis._pipeweld.result import WeldResult

# TODO conside a class structure with global state e.g. for instructions, compatible_config_groups, etc. to reduce complexity


def add(
    pipeline: Series,
    *,
    step: str,
    prerequisites: set[str] = set(),
    postrequisites: set[str] = set(),
    compatible_config_groups: set[str] = set(),
) -> WeldResult:
    if len(pipeline) == 0:
        # Empty pipeline
        return WeldResult(
            instructions=[InsertParallel(after=None, step=step)],
            solution=series(step),
        )

    partition, instructions = partition_component(
        pipeline,
        predecessor=None,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )

    rearranged_pipeline = _flatten_partition(partition)

    new_instructions = _insert_step(
        rearranged_pipeline,
        step=step,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
        compatible_config_groups=compatible_config_groups,
    )

    if not new_instructions:
        # Didn't find a pre-requisite so just add the step in parallel to everything
        new_instructions = _insert_before_postrequisites(
            rearranged_pipeline,
            idx=-1,
            predecessor=None,
            step=step,
            postrequisites=postrequisites,
            compatible_config_groups=compatible_config_groups,
        )

    instructions += new_instructions

    return WeldResult(
        solution=rearranged_pipeline,
        instructions=instructions,
    )


# TODO reduce complexity and enable ruff rules
def _insert_step(  # noqa: PLR0911, PLR0912
    component: Series,
    *,
    step: str,
    prerequisites: set[str],
    postrequisites: set[str],
    compatible_config_groups: set[str],
) -> list[BaseOperation]:
    # Iterate through the pipeline and insert the step
    # Work backwards until we find a pre-requisite (which is the final one), and then
    # insert after it - in parallel to its successor (or append if no successor). If we
    # don't find any pre-requsite then we insert in parallel to everything.
    for idx, subcomponent in reversed(list(enumerate(component.root))):
        if isinstance(subcomponent, str):
            if subcomponent in prerequisites:
                # Insert after this step
                if idx + 1 < len(component.root):
                    # i.e. there is a successor
                    return _insert_before_postrequisites(
                        component,
                        idx=idx,
                        predecessor=subcomponent,
                        step=step,
                        postrequisites=postrequisites,
                        compatible_config_groups=compatible_config_groups,
                    )
                else:
                    # i.e. there is no successor; append
                    component.root.append(step)
                    return [
                        InsertSuccessor(after=subcomponent, step=step)
                    ]  # TODO make sure this is tested
        elif isinstance(subcomponent, Series):
            added = _insert_step(
                subcomponent,
                step=step,
                prerequisites=prerequisites,
                postrequisites=postrequisites,
                compatible_config_groups=compatible_config_groups,
            )
            if added:
                return added
        elif isinstance(subcomponent, Parallel):
            added = _insert_step(
                Series(list(subcomponent.root)),
                step=step,
                prerequisites=prerequisites,
                postrequisites=postrequisites,
                compatible_config_groups=compatible_config_groups,
            )
            if added:
                return added
        elif isinstance(subcomponent, DepGroup):
            if subcomponent.config_group in compatible_config_groups:
                added = _insert_step(
                    subcomponent.series,
                    step=step,
                    prerequisites=prerequisites,
                    postrequisites=postrequisites,
                    compatible_config_groups=compatible_config_groups,
                )
                if added:
                    return added
            elif _has_any_steps(subcomponent, steps=prerequisites):
                added = _insert_before_postrequisites(
                    component,
                    idx=idx,
                    predecessor=get_endpoint(subcomponent),
                    step=step,
                    postrequisites=postrequisites,
                    compatible_config_groups=compatible_config_groups,
                )
                if added:
                    return added
        else:
            assert_never(subcomponent)

    return []


# TODO reduce complexity and enable ruff rule
def _insert_before_postrequisites(  # noqa: PLR0913
    component: Series,
    *,
    idx: int,
    predecessor: str | None,
    step: str,
    postrequisites: set[str],
    compatible_config_groups: set[str],
) -> list[BaseOperation]:
    successor_component = component.root[idx + 1]

    if isinstance(successor_component, Parallel) and len(successor_component.root) == 1:
        container = Series(list(successor_component.root))
        instructions = _insert_before_postrequisites(
            container,
            idx=-1,
            predecessor=predecessor,
            step=step,
            postrequisites=postrequisites,
            compatible_config_groups=compatible_config_groups,
        )
        if len(container) == 1 and container[0] == _union(successor_component, step):
            component[idx + 1] = _union(successor_component, step)

        return instructions
    elif isinstance(successor_component, Parallel | DepGroup | str):
        if _has_any_steps(successor_component, steps=postrequisites):
            # Insert before this step
            component.root.insert(idx + 1, step)
            return [InsertSuccessor(after=predecessor, step=step)]
        else:
            union = _union(successor_component, step)
            if union is None:
                raise AssertionError
            component.root[idx + 1] = union
            return [InsertParallel(after=predecessor, step=step)]
    elif isinstance(successor_component, Series):
        return _insert_before_postrequisites(
            successor_component,
            idx=-1,
            predecessor=predecessor,
            step=step,
            postrequisites=postrequisites,
            compatible_config_groups=compatible_config_groups,
        )
    else:
        assert_never(successor_component)


def _has_any_steps(
    component: Series | Parallel | DepGroup | str, *, steps: set[str]
) -> bool:
    if isinstance(component, str):
        return component in steps
    elif isinstance(component, Parallel | Series):
        for subcomponent in component.root:
            if _has_any_steps(subcomponent, steps=steps):
                return True
        return False
    elif isinstance(component, DepGroup):
        return _has_any_steps(component.series, steps=steps)
    else:
        assert_never(component)


class Partition(BaseModel):
    prerequisite_component: str | Series | DepGroup | Parallel | None = None
    nondependent_component: str | Series | DepGroup | Parallel | None = None
    postrequisite_component: str | Series | DepGroup | Parallel | None = None
    top_ranked_endpoint: str


def _flatten_partition(partition: Partition) -> Series:
    component = _concat(
        partition.prerequisite_component,
        partition.nondependent_component,
        partition.postrequisite_component,
    )
    if component is None:
        msg = "Flatten failed: no components"
        raise ValueError(msg)
    return component


@singledispatch
def partition_component(
    component: str | Series | Parallel,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[Partition, list[BaseOperation]]:
    raise NotImplementedError


@partition_component.register(str)
def _(
    component: str,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[Partition, list[BaseOperation]]:
    if component in prerequisites:
        return Partition(
            prerequisite_component=component,
            top_ranked_endpoint=component,
        ), []
    elif component in postrequisites:
        return Partition(
            postrequisite_component=component,
            top_ranked_endpoint=component,
        ), []
    else:
        return Partition(
            nondependent_component=component,
            top_ranked_endpoint=component,
        ), []


@partition_component.register(Parallel)
def _(
    component: Parallel,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[Partition, list[BaseOperation]]:
    partition_with_instruction_tuples = [
        partition_component(
            subcomponent,
            predecessor=predecessor,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )
        for subcomponent in component.root
    ]

    partitions = [_[0] for _ in partition_with_instruction_tuples]
    instructions = [x for _ in partition_with_instruction_tuples for x in _[1]]

    any_prerequisites = any(p.prerequisite_component is not None for p in partitions)
    any_postrequisites = any(p.postrequisite_component is not None for p in partitions)

    if any_prerequisites and any_postrequisites:
        return _parallel_merge_partitions(*partitions, predecessor=predecessor)
    elif any_prerequisites:
        return Partition(
            prerequisite_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        ), instructions
    elif any_postrequisites:
        return Partition(
            postrequisite_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        ), instructions
    else:
        return Partition(
            nondependent_component=component,
            top_ranked_endpoint=min(p.top_ranked_endpoint for p in partitions),
        ), instructions


@partition_component.register(Series)
def _(
    component: Series,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[Partition, list[BaseOperation]]:
    partitions, instructions = _get_series_partitions(
        component,
        predecessor=predecessor,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )
    if len(partitions) > 1:
        return reduce(_op_series_merge_partitions, partitions), instructions
    else:
        partition = partitions[0]
        return Partition(
            # TODO should this be series(DepGroup(...)) or do we need a special case?
            prerequisite_component=series(partition.prerequisite_component)
            if partition.prerequisite_component is not None
            else None,
            nondependent_component=series(partition.nondependent_component)
            if partition.nondependent_component is not None
            else None,
            postrequisite_component=series(partition.postrequisite_component)
            if partition.postrequisite_component is not None
            else None,
            top_ranked_endpoint=partition.top_ranked_endpoint,
        ), instructions


@partition_component.register(DepGroup)
def _(
    component: DepGroup,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[Partition, list[BaseOperation]]:
    partition, instructions = partition_component(
        component.series,
        predecessor=predecessor,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )
    partition = Partition(
        prerequisite_component=depgroup(
            partition.prerequisite_component, category=component.config_group
        )
        if partition.prerequisite_component is not None
        else None,
        nondependent_component=depgroup(
            partition.nondependent_component, category=component.config_group
        )
        if partition.nondependent_component is not None
        else None,
        postrequisite_component=depgroup(
            partition.postrequisite_component, category=component.config_group
        )
        if partition.postrequisite_component is not None
        else None,
        top_ranked_endpoint=partition.top_ranked_endpoint,
    )
    return partition, instructions


def _get_series_partitions(
    component: Series,
    *,
    predecessor: str | None,
    prerequisites: set[str],
    postrequisites: set[str],
) -> tuple[list[Partition], list[BaseOperation]]:
    partitions: list[Partition] = []
    instructions = []
    for subcomponent in component.root:
        partition, these_instructions = partition_component(
            subcomponent,
            predecessor=predecessor,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )
        partitions.append(partition)
        instructions.extend(these_instructions)
        predecessor = partition.top_ranked_endpoint  # For the next iteration

    return partitions, instructions


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
        # Element-wise concatenation
        if partition.prerequisite_component is None:
            prerequisite_component = next_partition.prerequisite_component
        elif next_partition.prerequisite_component is None:
            prerequisite_component = partition.prerequisite_component
        else:
            prerequisite_component = _concat(
                partition.prerequisite_component, next_partition.prerequisite_component
            )
        if partition.nondependent_component is None:
            nondependent_component = next_partition.nondependent_component
        elif next_partition.nondependent_component is None:
            nondependent_component = partition.nondependent_component
        else:
            nondependent_component = _concat(
                partition.nondependent_component, next_partition.nondependent_component
            )
        if partition.postrequisite_component is None:
            postrequisite_component = next_partition.postrequisite_component
        elif next_partition.postrequisite_component is None:
            postrequisite_component = partition.postrequisite_component
        else:
            postrequisite_component = _concat(
                partition.postrequisite_component,
                next_partition.postrequisite_component,
            )

        return Partition(
            prerequisite_component=prerequisite_component,
            nondependent_component=nondependent_component,
            postrequisite_component=postrequisite_component,
            top_ranked_endpoint=next_partition.top_ranked_endpoint,
        )


# TODO reduce the complexity of the below.
def _parallel_merge_partitions(  # noqa: PLR0912
    *partitions: Partition, predecessor: str | None
) -> tuple[Partition, list[BaseOperation]]:
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
    if prerequisite_components:
        prerequisite_component = _union(*prerequisite_components)
        if prerequisite_component is not None and len(prerequisite_component) == 1:
            # Collapse singleton
            (prerequisite_component,) = prerequisite_component.root
    else:
        prerequisite_component = None
    if nondependent_components:
        nondependent_component = _union(*nondependent_components)
        if nondependent_component is not None and len(nondependent_component) == 1:
            # Collapse singleton
            (nondependent_component,) = nondependent_component.root
    else:
        nondependent_component = None
    if postrequisite_components:
        postrequisite_component = _union(*postrequisite_components)
        if postrequisite_component is not None and len(postrequisite_component) == 1:
            # Collapse singleton
            (postrequisite_component,) = postrequisite_component.root
    else:
        postrequisite_component = None

    top_ranked_prerequisite_endpoints = [
        p.top_ranked_endpoint
        for p in partitions
        if p.prerequisite_component is not None
    ]
    top_ranked_nondependent_endpoints = [
        p.top_ranked_endpoint
        for p in partitions
        if p.nondependent_component is not None
    ]
    top_ranked_postrequisite_endpoints = [
        p.top_ranked_endpoint
        for p in partitions
        if p.postrequisite_component is not None
    ]
    top_ranked_endpoint = min(
        top_ranked_postrequisite_endpoints
        or top_ranked_nondependent_endpoints
        or top_ranked_prerequisite_endpoints
    )

    instructions = []
    if prerequisite_component is not None:
        new_instructions, _ = _get_instructions_insert_successor(
            prerequisite_component, after=predecessor
        )
        instructions.extend(new_instructions)
    if nondependent_component is not None:
        if prerequisite_component is not None:
            after = get_endpoint(prerequisite_component)
        else:
            after = predecessor
        new_instructions, _ = _get_instructions_insert_successor(
            nondependent_component, after=after
        )
        instructions.extend(new_instructions)
    if postrequisite_component is not None:
        if nondependent_component is not None:
            after = get_endpoint(nondependent_component)
        elif prerequisite_component is not None:
            after = get_endpoint(prerequisite_component)
        else:
            after = predecessor
        new_instructions, _ = _get_instructions_insert_successor(
            postrequisite_component, after=after
        )
        instructions.extend(new_instructions)

    return Partition(
        prerequisite_component=prerequisite_component,
        nondependent_component=nondependent_component,
        postrequisite_component=postrequisite_component,
        top_ranked_endpoint=top_ranked_endpoint,
    ), instructions


def _get_instructions_insert_successor(
    component: Series | Parallel | DepGroup | str, *, after: str | None
) -> tuple[list[BaseOperation], str | None]:
    if isinstance(component, str):
        return [InsertSuccessor(after=after, step=component)], component
    elif isinstance(component, Series):
        instructions = []
        for idx, subcomponent in enumerate(component.root):
            new_instructions, endpoint = _get_instructions_insert_successor(
                subcomponent, after=after
            )
            instructions.extend(new_instructions)
            after = endpoint
        return instructions, after
    elif isinstance(component, Parallel):
        instructions: list[BaseOperation] = []
        endpoints = []
        min_idx = None
        min_endpoint = None
        for idx, subcomponent in enumerate(component.root):
            new_instructions, endpoint = _get_instructions_insert_successor(
                subcomponent,
                after=after,
            )
            if endpoint is not None and (
                min_endpoint is None or endpoint < min_endpoint
            ):
                min_idx = idx
                min_endpoint = endpoint

            endpoints.append(endpoint)
            instructions.extend(new_instructions)

        if min_idx is None:
            msg = "The endpoint of all parallel subcomponents were None unexpectedly"
            raise AssertionError(msg)

        instructions[min_idx] = InsertParallel(
            after=instructions[min_idx].after, step=instructions[min_idx].step
        )

        sorted_idxs = sorted(range(len(endpoints)), key=lambda k: endpoints[k])

        instructions = [instructions[idx] for idx in sorted_idxs]

        return instructions, min(endpoints)
    elif isinstance(component, DepGroup):
        return _get_instructions_insert_successor(
            component.series,
            after=after,
        )
    else:
        assert_never(component)


def _concat(*components: str | Series | DepGroup | Parallel | None) -> Series | None:
    s = []
    for component in components:
        if isinstance(component, Series):
            s.extend(component.root)
        elif isinstance(component, Parallel | str):
            s.append(component)
        elif component is None:
            pass
        elif isinstance(component, DepGroup):
            s.append(component)
        else:
            assert_never(component)

    if not s:
        return None

    return series(*s)


def _union(*components: str | Series | DepGroup | Parallel | None) -> Parallel | None:
    p = []
    for component in components:
        if isinstance(component, Parallel):
            p.extend(component.root)
        elif isinstance(component, Series | str):
            p.append(component)
        elif component is None:
            pass
        elif isinstance(component, DepGroup):
            p.append(component)
        else:
            assert_never(component)

    if not p:
        return None

    return parallel(*p)


def get_endpoint(component: str | Series | DepGroup | Parallel) -> str:
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
    elif isinstance(component, DepGroup):
        return get_endpoint(component.series)
    else:
        assert_never(component)
