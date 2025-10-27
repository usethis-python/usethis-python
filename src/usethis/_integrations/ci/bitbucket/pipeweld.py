from __future__ import annotations

from functools import singledispatch
from typing import TYPE_CHECKING
from uuid import uuid4

from typing_extensions import assert_never

import usethis._pipeweld.containers
from usethis._integrations.ci.bitbucket.dump import bitbucket_fancy_dump
from usethis._integrations.ci.bitbucket.errors import UnexpectedImportPipelineError
from usethis._integrations.ci.bitbucket.io_ import (
    edit_bitbucket_pipelines_yaml,
)
from usethis._integrations.ci.bitbucket.schema import (
    ImportPipeline,
    Items,
    Parallel,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Pipeline,
    Pipelines,
    StageItem,
    StepItem,
)
from usethis._integrations.ci.bitbucket.schema_utils import step1tostep
from usethis._integrations.file.yaml.update import update_ruamel_yaml_map
from usethis._pipeweld.ops import InsertParallel, InsertSuccessor, Instruction

if TYPE_CHECKING:
    from usethis._integrations.ci.bitbucket.io_ import (
        BitbucketPipelinesYAMLDocument,
    )
    from usethis._integrations.ci.bitbucket.schema import (
        PipelinesConfiguration,
        Step,
    )


def get_pipeweld_step(step: Step) -> str:
    if step.name is not None:
        return step.name
    return step.model_dump_json(exclude_defaults=True)


def get_pipeweld_pipeline_from_default(
    model: PipelinesConfiguration,
) -> usethis._pipeweld.containers.Series:
    if model.pipelines is None:
        model.pipelines = Pipelines()
    default = model.pipelines.default

    if default is None:
        items = []
    elif isinstance(default.root, ImportPipeline):
        msg = (
            "Cannot add step to default pipeline in 'bitbucket-pipelines.yml' because "
            "it is an import pipeline."
        )
        raise UnexpectedImportPipelineError(msg)
    else:
        items = default.root.root

    return usethis._pipeweld.containers.series(
        *[get_pipeweld_object(item) for item in items]
    )


@singledispatch
def get_pipeweld_object(
    item: StepItem | ParallelItem | StageItem,
) -> (
    str | usethis._pipeweld.containers.Parallel | usethis._pipeweld.containers.DepGroup
):
    raise NotImplementedError


@get_pipeweld_object.register
def _(item: StepItem):
    return get_pipeweld_step(item.step)


@get_pipeweld_object.register
def _(item: ParallelItem):
    parallel_steps: set[str] = set()

    if item.parallel is not None:
        if isinstance(item.parallel.root, ParallelSteps):
            step_items = item.parallel.root.root
        elif isinstance(item.parallel.root, ParallelExpanded):
            step_items = item.parallel.root.steps.root
        else:
            assert_never(item.parallel.root)

        for step_item in step_items:
            parallel_steps.add(get_pipeweld_step(step_item.step))

    return usethis._pipeweld.containers.Parallel(frozenset(parallel_steps))


@get_pipeweld_object.register
def _(item: StageItem):
    depgroup_steps: list[str] = []

    if item.stage.name is not None:
        name = item.stage.name
    else:
        name = str(f"Unnamed Stage {uuid4()}")

    for step in item.stage.steps:
        depgroup_steps.append(get_pipeweld_step(step1tostep(step)))

    return usethis._pipeweld.containers.DepGroup(
        series=usethis._pipeweld.containers.series(*depgroup_steps),
        config_group=name,
    )


def apply_pipeweld_instruction(instruction: Instruction, *, new_step: Step) -> None:
    with edit_bitbucket_pipelines_yaml() as doc:
        apply_pipeweld_instruction_via_doc(instruction, doc=doc, new_step=new_step)
        dump = bitbucket_fancy_dump(doc.model, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)


def apply_pipeweld_instruction_via_doc(
    instruction: Instruction,
    *,
    new_step: Step,
    doc: BitbucketPipelinesYAMLDocument,
) -> None:
    if get_pipeweld_step(new_step) != instruction.step:
        # N.B. This doesn't currently handle moving existing steps
        return

    if doc.model.pipelines is None:
        doc.model.pipelines = Pipelines()

    pipelines = doc.model.pipelines
    default = pipelines.default

    if default is None:
        items = []
    elif isinstance(default.root, ImportPipeline):
        msg = (
            f"Cannot add step '{new_step.name}' to default pipeline in "
            f"'bitbucket-pipelines.yml' because it is an import pipeline."
        )
        raise UnexpectedImportPipelineError(msg)
    else:
        items = default.root.root

    if instruction.after is None:
        # Insert at the beginning - always as a simple step
        items.insert(0, StepItem(step=new_step))
    elif isinstance(instruction, InsertSuccessor):
        # Insert in series after the specified step
        for item in items:
            if _is_insertion_necessary(item, instruction=instruction):
                items.insert(
                    items.index(item) + 1,
                    StepItem(step=new_step),
                )
                break
    elif isinstance(instruction, InsertParallel):
        # Insert in parallel with the specified step
        for idx, item in enumerate(items):
            if _is_insertion_necessary(item, instruction=instruction):
                _insert_parallel_step(items, idx, item, new_step)
                break

    if default is None and items:
        pipelines.default = Pipeline(Items(items))


@singledispatch
def _insert_parallel_step(
    items: list[StepItem | ParallelItem | StageItem],
    idx: int,
    item: StepItem | ParallelItem | StageItem,
    new_step: "Step",
) -> None:
    """Insert a step in parallel with an existing item.
    
    This function handles the logic of converting a single step to a parallel block
    or adding to an existing parallel block.
    """
    raise NotImplementedError


@_insert_parallel_step.register
def _(items, idx, item: StepItem, new_step):
    """Convert a single StepItem to a ParallelItem with both steps."""
    # Replace the single step with a parallel block containing both steps
    parallel_item = ParallelItem(
        parallel=Parallel(
            ParallelSteps([
                StepItem(step=item.step),
                StepItem(step=new_step),
            ])
        )
    )
    items[idx] = parallel_item


@_insert_parallel_step.register
def _(items, idx, item: ParallelItem, new_step):
    """Add a new step to an existing ParallelItem."""
    if item.parallel is not None:
        if isinstance(item.parallel.root, ParallelSteps):
            # Add to the existing list of parallel steps
            item.parallel.root.root.append(StepItem(step=new_step))
        elif isinstance(item.parallel.root, ParallelExpanded):
            # Add to the expanded parallel steps
            item.parallel.root.steps.root.append(StepItem(step=new_step))
        else:
            assert_never(item.parallel.root)


@_insert_parallel_step.register
def _(items, idx, item: StageItem, new_step):
    """Insert parallel step after a stage item.
    
    Since we found the target step within a stage, we can't insert in parallel
    with it (stages don't support parallelism within them). Instead, we insert
    a new step in parallel with the entire stage.
    """
    # Create a parallel block with the stage and the new step
    parallel_item = ParallelItem(
        parallel=Parallel(
            ParallelSteps([
                item,  # The entire stage
                StepItem(step=new_step),
            ])
        )
    )
    items[idx] = parallel_item


@singledispatch
def _is_insertion_necessary(
    item: StepItem | ParallelItem | StageItem,
    *,
    instruction: Instruction,
) -> bool:
    raise NotImplementedError


@_is_insertion_necessary.register
def _(item: StepItem, *, instruction: Instruction):
    return get_pipeweld_step(item.step) == instruction.after


@_is_insertion_necessary.register
def _(item: ParallelItem, *, instruction: Instruction):
    if item.parallel is not None:
        if isinstance(item.parallel.root, ParallelSteps):
            step_items = item.parallel.root.root
        elif isinstance(item.parallel.root, ParallelExpanded):
            step_items = item.parallel.root.steps.root
        else:
            assert_never(item.parallel.root)

        for step_item in step_items:
            if get_pipeweld_step(step_item.step) == instruction.after:
                return True
    return False


@_is_insertion_necessary.register
def _(item: StageItem, *, instruction: Instruction):
    step1s = item.stage.steps.copy()

    for step1 in step1s:
        step = step1tostep(step1)

        if get_pipeweld_step(step) == instruction.after:
            return True

    return False
