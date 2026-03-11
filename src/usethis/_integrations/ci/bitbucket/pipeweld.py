from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from typing_extensions import assert_never

import usethis._pipeweld.containers
from usethis._integrations.ci.bitbucket import schema
from usethis._integrations.ci.bitbucket.errors import (
    MissingStepError,
    UnexpectedImportPipelineError,
)
from usethis._integrations.ci.bitbucket.init import (
    ensure_bitbucket_pipelines_config_exists,
)
from usethis._integrations.ci.bitbucket.schema_utils import step1tostep
from usethis._integrations.ci.bitbucket.yaml import BitbucketPipelinesYAMLManager
from usethis._pipeweld.ops import InsertParallel, InsertSuccessor

if TYPE_CHECKING:
    from usethis._pipeweld.ops import Instruction


def get_pipeweld_step(step: schema.Step) -> str:
    if step.name is not None:
        return step.name
    return step.model_dump_json(exclude_defaults=True, by_alias=True)


def get_pipeweld_pipeline_from_default(
    model: schema.PipelinesConfiguration,
) -> usethis._pipeweld.containers.Series:
    if model.pipelines is None:
        model.pipelines = schema.Pipelines()
    default = model.pipelines.default

    if default is None:
        items = []
    elif isinstance(default.root, schema.ImportPipeline):
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


def get_pipeweld_object(
    item: schema.StepItem | schema.ParallelItem | schema.StageItem,
) -> (
    str | usethis._pipeweld.containers.Parallel | usethis._pipeweld.containers.DepGroup
):
    if isinstance(item, schema.StepItem):
        return get_pipeweld_step(item.step)
    elif isinstance(item, schema.ParallelItem):
        parallel_steps: set[str] = set()

        if item.parallel is not None:
            if isinstance(item.parallel.root, schema.ParallelSteps):
                step_items = item.parallel.root.root
            elif isinstance(item.parallel.root, schema.ParallelExpanded):
                step_items = item.parallel.root.steps.root
            else:
                assert_never(item.parallel.root)

            for step_item in step_items:
                parallel_steps.add(get_pipeweld_step(step_item.step))

        return usethis._pipeweld.containers.Parallel(frozenset(parallel_steps))
    elif isinstance(item, schema.StageItem):
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
    else:
        assert_never(item)


def apply_pipeweld_instruction(
    instruction: Instruction, *, step_to_insert: schema.Step
) -> None:
    ensure_bitbucket_pipelines_config_exists()

    mgr = BitbucketPipelinesYAMLManager()
    model = mgr.model_validate()
    apply_pipeweld_instruction_via_model(
        instruction, model=model, step_to_insert=step_to_insert
    )
    mgr.commit_model(model)


def apply_pipeweld_instruction_via_model(
    instruction: Instruction,
    *,
    step_to_insert: schema.Step,
    model: schema.PipelinesConfiguration,
) -> None:
    if model.pipelines is None:
        model.pipelines = schema.Pipelines()

    pipelines = model.pipelines
    default = pipelines.default

    if default is None:
        items = []
    elif isinstance(default.root, schema.ImportPipeline):
        msg = (
            f"Cannot add step '{step_to_insert.name}' to default pipeline in "
            f"'bitbucket-pipelines.yml' because it is an import pipeline."
        )
        raise UnexpectedImportPipelineError(msg)
    else:
        items = default.root.root

    # Check if this instruction is for a new step or an existing step
    # When pipeweld determines we need to add a step (e.g., adding "lint" step to a pipeline),
    # it generates instructions for how to insert it. If the pipeline already has steps in
    # parallel that need to be rearranged to satisfy dependencies, pipeweld also generates
    # instructions to move those existing steps. So:
    # - New step: inserting the actual new step being added (e.g., "lint")
    # - Existing step: rearranging an existing step (e.g., moving "build" from a parallel
    #   block so "lint" can be inserted between "build" and "test")
    try:
        # Try to extract an existing step with this name
        step = _extract_step_from_items(items, step_name=instruction.step)
    except MissingStepError:
        # Step not found in pipeline, so this must be the new step being added
        step = step_to_insert

    _apply_instruction_to_items(
        instruction=instruction, items=items, step_to_insert=step
    )

    if default is None and items:
        pipelines.default = schema.Pipeline(schema.Items(items))


def _apply_instruction_to_items(
    *,
    instruction: Instruction,
    items: list[schema.StepItem | schema.ParallelItem | schema.StageItem],
    step_to_insert: schema.Step,
) -> None:
    """Apply an instruction to insert a step into the items list.

    Args:
        instruction: The instruction specifying how to insert the step.
        items: The list of pipeline items to modify.
        step_to_insert: The step to insert.
    """
    if instruction.after is None:
        # Insert at the beginning - always as a simple step
        items.insert(0, schema.StepItem(step=step_to_insert))
    elif isinstance(instruction, InsertSuccessor):
        # Insert in series after the specified step
        for item in items:
            if _is_insertion_necessary(item, instruction=instruction):
                items.insert(
                    items.index(item) + 1,
                    schema.StepItem(step=step_to_insert),
                )
                break
    elif isinstance(instruction, InsertParallel):
        # Insert in parallel with the specified step
        for idx, item in enumerate(items):
            if _is_insertion_necessary(item, instruction=instruction):
                _insert_parallel_step(
                    item, items=items, idx=idx, step_to_insert=step_to_insert
                )
                break
    else:
        assert_never(instruction)


def _extract_step_from_items(
    items: list[schema.StepItem | schema.ParallelItem | schema.StageItem],
    *,
    step_name: str,
) -> schema.Step:
    """Find and remove a step from the items list.

    This function searches for a step with the given name, removes it from the
    items list, and returns the step. If the step is found in a parallel block
    with other steps, only that step is removed from the parallel block.

    Raises:
        MissingStepError: If the step cannot be found in the pipeline.
    """
    for idx, item in enumerate(items):
        extracted = _extract_step_from_item(
            item, step_name=step_name, items=items, idx=idx
        )
        if extracted is not None:
            return extracted
    msg = f"Step '{step_name}' not found in pipeline"
    raise MissingStepError(msg)


def _extract_step_from_item(
    item: schema.StepItem | schema.ParallelItem | schema.StageItem,
    *,
    step_name: str,
    items: list[schema.StepItem | schema.ParallelItem | schema.StageItem],
    idx: int,
) -> schema.Step | None:
    """Extract a step from an item, potentially modifying the items list."""
    if isinstance(item, schema.StepItem):
        if get_pipeweld_step(item.step) == step_name:
            # Remove this item from the list
            items.pop(idx)
            return item.step
        return None
    elif isinstance(item, schema.ParallelItem):
        return _extract_step_from_parallel_item(
            item, step_name=step_name, items=items, idx=idx
        )
    elif isinstance(item, schema.StageItem):
        # We don't extract steps from within stages as they represent deployment
        # stages and their internal structure should be preserved.
        return None
    else:
        assert_never(item)


def _extract_step_from_parallel_item(
    item: schema.ParallelItem,
    *,
    step_name: str,
    items: list[schema.StepItem | schema.ParallelItem | schema.StageItem],
    idx: int,
) -> schema.Step | None:
    if item.parallel is not None:
        if isinstance(item.parallel.root, schema.ParallelSteps):
            step_items = item.parallel.root.root
        elif isinstance(item.parallel.root, schema.ParallelExpanded):
            step_items = item.parallel.root.steps.root
        else:
            assert_never(item.parallel.root)

        for step_idx, step_item in enumerate(step_items):
            if get_pipeweld_step(step_item.step) == step_name:
                # Found it - remove from the parallel block
                extracted_step = step_item.step
                step_items.pop(step_idx)

                # If only one step remains in the parallel, convert to a simple step
                if len(step_items) == 1:
                    items[idx] = step_items[0]
                elif len(step_items) == 0:
                    # No steps left, remove the parallel item
                    items.pop(idx)

                return extracted_step
    return None


def _insert_parallel_step(
    item: schema.StepItem | schema.ParallelItem | schema.StageItem,
    *,
    items: list[schema.StepItem | schema.ParallelItem | schema.StageItem],
    idx: int,
    step_to_insert: schema.Step,
) -> None:
    """Insert a step in parallel with an existing item.

    This function handles the logic of converting a single step to a parallel block
    or adding to an existing parallel block.
    """
    if isinstance(item, schema.StepItem):
        # Replace the single step with a parallel block containing both steps
        parallel_item = schema.ParallelItem(
            parallel=schema.Parallel(
                schema.ParallelSteps(
                    [
                        schema.StepItem(step=item.step),
                        schema.StepItem(step=step_to_insert),
                    ]
                )
            )
        )
        items[idx] = parallel_item
    elif isinstance(item, schema.ParallelItem):
        if item.parallel is not None:
            if isinstance(item.parallel.root, schema.ParallelSteps):
                # Add to the existing list of parallel steps
                item.parallel.root.root.append(schema.StepItem(step=step_to_insert))
            elif isinstance(item.parallel.root, schema.ParallelExpanded):
                # Add to the expanded parallel steps
                item.parallel.root.steps.root.append(schema.StepItem(step=step_to_insert))
            else:
                assert_never(item.parallel.root)
    elif isinstance(item, schema.StageItem):
        # StageItems are trickier since they aren't supported in ParallelSteps. But we
        # never need to add them in practice anyway. The only reason this is really here
        # is for type safety.
        raise NotImplementedError
    else:
        assert_never(item)


def _is_insertion_necessary(
    item: schema.StepItem | schema.ParallelItem | schema.StageItem,
    *,
    instruction: Instruction,
) -> bool:
    if isinstance(item, schema.StepItem):
        return get_pipeweld_step(item.step) == instruction.after
    elif isinstance(item, schema.ParallelItem):
        if item.parallel is not None:
            if isinstance(item.parallel.root, schema.ParallelSteps):
                step_items = item.parallel.root.root
            elif isinstance(item.parallel.root, schema.ParallelExpanded):
                step_items = item.parallel.root.steps.root
            else:
                assert_never(item.parallel.root)

            for step_item in step_items:
                if get_pipeweld_step(step_item.step) == instruction.after:
                    return True
        return False
    elif isinstance(item, schema.StageItem):
        step1s = item.stage.steps.copy()

        for step1 in step1s:
            step = step1tostep(step1)

            if get_pipeweld_step(step) == instruction.after:
                return True

        return False
    else:
        assert_never(item)
