from __future__ import annotations

import contextlib
from functools import reduce, singledispatch, singledispatchmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel
from typing_extensions import assert_never

from usethis._pipeweld.containers import (
    DepGroup,
    Parallel,
    Series,
    depgroup,
    parallel,
    series,
)
from usethis._pipeweld.ops import InsertParallel, InsertSuccessor
from usethis._pipeweld.result import WeldResult

if TYPE_CHECKING:
    from usethis._pipeweld.ops import Instruction


class Partition(BaseModel):
    prerequisite_component: str | Series | DepGroup | Parallel | None = None
    nondependent_component: str | Series | DepGroup | Parallel | None = None
    postrequisite_component: str | Series | DepGroup | Parallel | None = None
    top_ranked_endpoint: str


class Adder(BaseModel):
    pipeline: Series
    step: str
    prerequisites: set[str] = set()
    postrequisites: set[str] = set()
    compatible_config_groups: set[str] = set()

    def add(self) -> WeldResult:
        if len(self.pipeline) == 0:
            # Empty pipeline
            return WeldResult(
                instructions=[InsertParallel(after=None, step=self.step)],
                solution=series(self.step),
            )

        partition, instructions = self.partition_component(
            self.pipeline, predecessor=None
        )
        rearranged_pipeline = _flatten_partition(partition)
        new_instructions = self._insert_step(rearranged_pipeline)

        if not new_instructions:
            # Didn't find a pre-requisite so just add the step in parallel to everything
            new_instructions = self._insert_before_postrequisites(
                rearranged_pipeline, idx=-1, predecessor=None
            )

        instructions += new_instructions

        return WeldResult(
            solution=rearranged_pipeline,
            instructions=instructions,
        )

    @singledispatchmethod
    def partition_component(
        self, component: str | Series | Parallel | DepGroup, *, predecessor: str | None
    ) -> tuple[Partition, list[Instruction]]:
        raise NotImplementedError

    @partition_component.register(str)
    def _(
        self, component: str, *, predecessor: str | None
    ) -> tuple[Partition, list[Instruction]]:
        if component in self.prerequisites:
            return Partition(
                prerequisite_component=component,
                top_ranked_endpoint=component,
            ), []
        elif component in self.postrequisites:
            return Partition(
                postrequisite_component=component,
                top_ranked_endpoint=component,
            ), []
        else:
            return Partition(
                nondependent_component=component,
                top_ranked_endpoint=component,
            ), []

    @partition_component.register(Series)
    def _(
        self, component: Series, *, predecessor: str | None
    ) -> tuple[Partition, list[Instruction]]:
        partitions: list[Partition] = []
        instructions = []
        for subcomponent in component.root:
            partition, these_instructions = self.partition_component(
                subcomponent,
                predecessor=predecessor,
            )
            partitions.append(partition)
            instructions.extend(these_instructions)
            predecessor = partition.top_ranked_endpoint  # For the next iteration

        if len(partitions) > 1:
            return reduce(_op_series_merge_partitions, partitions), instructions
        else:
            partition = partitions[0]
            return Partition(
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

    @partition_component.register(Parallel)
    def _(
        self, component: Parallel, *, predecessor: str | None
    ) -> tuple[Partition, list[Instruction]]:
        partition_with_instruction_tuples = [
            self.partition_component(
                subcomponent,
                predecessor=predecessor,
            )
            for subcomponent in component.root
        ]

        partitions = [_[0] for _ in partition_with_instruction_tuples]
        instructions = [x for _ in partition_with_instruction_tuples for x in _[1]]

        any_prerequisites = any(
            p.prerequisite_component is not None for p in partitions
        )
        any_postrequisites = any(
            p.postrequisite_component is not None for p in partitions
        )

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

    @partition_component.register(DepGroup)
    def _(
        self, component: DepGroup, *, predecessor: str | None
    ) -> tuple[Partition, list[Instruction]]:
        partition, instructions = self.partition_component(
            component.series,
            predecessor=predecessor,
        )
        partition = Partition(
            prerequisite_component=depgroup(
                partition.prerequisite_component, config_group=component.config_group
            )
            if partition.prerequisite_component is not None
            else None,
            nondependent_component=depgroup(
                partition.nondependent_component, config_group=component.config_group
            )
            if partition.nondependent_component is not None
            else None,
            postrequisite_component=depgroup(
                partition.postrequisite_component, config_group=component.config_group
            )
            if partition.postrequisite_component is not None
            else None,
            top_ranked_endpoint=partition.top_ranked_endpoint,
        )
        return partition, instructions

    def _insert_step(
        self,
        component: Series,
    ) -> list[Instruction]:
        # Iterate through the pipeline and insert the step
        # Work backwards until we find a pre-requisite (which is the final one), and then
        # insert after it - in parallel to its successor (or append if no successor). If we
        # don't find any pre-requsite then we insert in parallel to everything.
        for idx, subcomponent in reversed(list(enumerate(component.root))):
            if isinstance(subcomponent, str):
                if subcomponent in self.prerequisites:
                    return self._insert_before_postrequisites(
                        component,
                        idx=idx,
                        predecessor=subcomponent,
                    )
            elif isinstance(subcomponent, Series):
                added = self._insert_step(subcomponent)
                if added:
                    return added
            elif isinstance(subcomponent, Parallel):
                added = self._insert_step(Series(list(subcomponent.root)))
                if added:
                    return added
            elif isinstance(subcomponent, DepGroup):
                if _has_any_steps(subcomponent, steps=self.prerequisites):
                    added = self._insert_before_postrequisites(
                        component,
                        idx=idx,
                        predecessor=get_endpoint(subcomponent),
                    )
                    if added:
                        return added
            else:
                assert_never(subcomponent)

        return []

    def _insert_before_postrequisites(
        self, component: Series, *, idx: int, predecessor: str | None
    ) -> list[Instruction]:
        if idx + 1 >= len(component.root):
            # i.e. there is no successor; append
            component.root.append(self.step)
            return [InsertSuccessor(after=predecessor, step=self.step)]

        successor_component = component.root[idx + 1]

        if (
            isinstance(successor_component, Parallel)
            and len(successor_component.root) == 1
        ):
            container = Series(list(successor_component.root))
            instructions = self._insert_before_postrequisites(
                container,
                idx=-1,
                predecessor=predecessor,
            )
            if len(container) == 1 and container[0] == _union(
                successor_component, self.step
            ):
                component[idx + 1] = _union(successor_component, self.step)

            return instructions
        elif isinstance(successor_component, Parallel | DepGroup | str):
            if _has_any_steps(successor_component, steps=self.postrequisites):
                # Insert before this step
                component.root.insert(idx + 1, self.step)
                return [InsertSuccessor(after=predecessor, step=self.step)]
            else:
                union = _union(successor_component, self.step)
                if union is None:
                    raise AssertionError
                component.root[idx + 1] = union
                return [InsertParallel(after=predecessor, step=self.step)]
        elif isinstance(successor_component, Series):
            return self._insert_before_postrequisites(
                successor_component,
                idx=-1,
                predecessor=predecessor,
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


def _flatten_partition(partition: Partition) -> Series:
    component = _concat(
        partition.prerequisite_component,
        partition.nondependent_component,
        partition.postrequisite_component,
    )
    if component is None:
        msg = "Flatten failed: no components."
        raise ValueError(msg)
    return component


def _op_series_merge_partitions(
    partition: Partition, next_partition: Partition
) -> Partition:
    if next_partition.prerequisite_component is not None:
        return Partition(
            # N.B. this concat will never be singleton since at least one of the LHS
            # partitions will have a non-None prerequisite_component, and this branch of
            # the if-else will only be taken if the next_partition has a non-None
            # prerequisite_component too.
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
        if partition.prerequisite_component is not None:
            prerequisite_component = partition.prerequisite_component
        else:
            prerequisite_component = None

        return Partition(
            prerequisite_component=prerequisite_component,
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
        else:
            prerequisite_component = partition.prerequisite_component

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


def _parallel_merge_partitions(
    *partitions: Partition, predecessor: str | None
) -> tuple[Partition, list[Instruction]]:
    # Element-wise parallelism
    prerequisite_component = _collapsed_union(
        *[p.prerequisite_component for p in partitions]
    )
    nondependent_component = _collapsed_union(
        *[p.nondependent_component for p in partitions]
    )
    postrequisite_component = _collapsed_union(
        *[p.postrequisite_component for p in partitions]
    )

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
        new_instructions, _ = _get_instructions_for_insertion(
            prerequisite_component, after=predecessor
        )
        instructions.extend(new_instructions)
    if nondependent_component is not None:
        if prerequisite_component is not None:
            after = get_endpoint(prerequisite_component)
        else:
            after = predecessor
        new_instructions, _ = _get_instructions_for_insertion(
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
        new_instructions, _ = _get_instructions_for_insertion(
            postrequisite_component, after=after
        )
        instructions.extend(new_instructions)

    return Partition(
        prerequisite_component=prerequisite_component,
        nondependent_component=nondependent_component,
        postrequisite_component=postrequisite_component,
        top_ranked_endpoint=top_ranked_endpoint,
    ), instructions


def _collapsed_union(
    *components: str | Series | DepGroup | Parallel | None,
) -> str | Series | DepGroup | Parallel | None:
    component = _union(*components)
    if component is not None and len(component) == 1:
        # Collapse singleton
        (component,) = component.root
    return component


@singledispatch
def _get_instructions_for_insertion(
    component: str | Series | Parallel | DepGroup, *, after: str | None
) -> tuple[list[Instruction], str | None]:
    """Get the instructions to insert a component after the given step.

    The instructions are given as individual step-by-step insertions.

    Args:
        component: The component to insert.
        after: The step to insert the new component after.

    Returns:
        A tuple containing the instructions to insert the new component and the endpoint
        of the component after the new step has been inserted.
    """
    raise NotImplementedError


@_get_instructions_for_insertion.register(str)
def _(component: str, *, after: str | None) -> tuple[list[Instruction], str | None]:
    return [InsertSuccessor(after=after, step=component)], component


@_get_instructions_for_insertion.register(Series)
def _(component: Series, *, after: str | None) -> tuple[list[Instruction], str | None]:
    instructions = []
    for subcomponent in component.root:
        new_instructions, endpoint = _get_instructions_for_insertion(
            subcomponent, after=after
        )
        instructions.extend(new_instructions)
        after = endpoint
    return instructions, after


@_get_instructions_for_insertion.register(Parallel)
def _(
    component: Parallel, *, after: str | None
) -> tuple[list[Instruction], str | None]:
    if len(component.root) == 0:
        return [], after

    instructions: list[Instruction] = []
    endpoints = []
    min_idx = None
    min_endpoint = None
    for idx, subcomponent in enumerate(component.root):
        new_instructions, endpoint = _get_instructions_for_insertion(
            subcomponent,
            after=after,
        )
        if endpoint is not None and (min_endpoint is None or endpoint < min_endpoint):
            min_idx = idx
            min_endpoint = endpoint

        endpoints.append(endpoint)
        instructions.extend(new_instructions)

    for idx in range(len(component.root)):
        if idx != min_idx:
            instructions[idx] = InsertParallel(
                after=instructions[idx].after, step=instructions[idx].step
            )

    sorted_idxs = sorted(range(len(endpoints)), key=lambda k: endpoints[k])

    instructions = [instructions[idx] for idx in sorted_idxs]

    return instructions, min(endpoints)


@_get_instructions_for_insertion.register(DepGroup)
def _(
    component: DepGroup, *, after: str | None
) -> tuple[list[Instruction], str | None]:
    return _get_instructions_for_insertion(
        component.series,
        after=after,
    )


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

        msg = "No endpoints are defined for a Series with no steps."
        raise ValueError(msg)
    elif isinstance(component, Parallel):
        endpoints = []
        for subcomponent in component.root:
            with contextlib.suppress(ValueError):
                endpoints.append(get_endpoint(subcomponent))
        # Any endpoint will do so choose the first one
        # alphabetically
        if not endpoints:
            msg = "No endpoints are defined for a Parallel block with no steps."
            raise ValueError(msg)
        return sorted(endpoints)[0]
    elif isinstance(component, DepGroup):
        return get_endpoint(component.series)
    else:
        assert_never(component)
