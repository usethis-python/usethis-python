from __future__ import annotations

from functools import singledispatch
from typing import TYPE_CHECKING, cast

from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.scalarstring import LiteralScalarString
from typing_extensions import assert_never

import usethis._pipeweld.func
from usethis._config import usethis_config
from usethis._console import instruct_print, tick_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor,
    anchor_name_from_script_item,
)
from usethis._integrations.ci.bitbucket.cache import _add_caches_via_model, remove_cache
from usethis._integrations.ci.bitbucket.errors import (
    UnexpectedImportPipelineError,
)
from usethis._integrations.ci.bitbucket.init import (
    ensure_bitbucket_pipelines_config_exists,
)
from usethis._integrations.ci.bitbucket.pipeweld import (
    apply_pipeweld_instruction_via_model,
    get_pipeweld_pipeline_from_default,
    get_pipeweld_step,
)
from usethis._integrations.ci.bitbucket.schema import (
    CachePath,
    Definitions,
    ImportPipeline,
    Parallel,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Script,
    StageItem,
    Step,
    StepItem,
)
from usethis._integrations.ci.bitbucket.schema_utils import step1tostep
from usethis._integrations.ci.bitbucket.yaml import BitbucketPipelinesYAMLManager
from usethis._integrations.environ.python import get_supported_minor_python_versions
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from ruamel.yaml.anchor import Anchor

    from usethis._integrations.ci.bitbucket.anchor import ScriptItemName
    from usethis._integrations.ci.bitbucket.schema import (
        Pipeline,
        PipelinesConfiguration,
    )
    from usethis._integrations.file.yaml.io_ import YAMLDocument


_CACHE_LOOKUP = {
    "uv": CachePath("~/.cache/uv"),
    "pre-commit": CachePath("~/.cache/pre-commit"),
}


_PLACEHOLDER_NAME = "Placeholder - add your own steps!"

_SCRIPT_ITEM_LOOKUP: dict[ScriptItemName, LiteralScalarString] = {
    "install-uv": LiteralScalarString("""\
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
export UV_LINK_MODE=copy
uv --version
"""),
    "ensure-venv": LiteralScalarString("""\
python -m venv .venv
source .venv/bin/activate
"""),
}
for name, script_item in _SCRIPT_ITEM_LOOKUP.items():
    script_item.yaml_set_anchor(value=name, always_dump=True)


def add_bitbucket_step_in_default(step: Step) -> None:
    ensure_bitbucket_pipelines_config_exists()

    try:
        existing_steps = get_steps_in_default()
    except UnexpectedImportPipelineError:
        msg = (
            f"Cannot add step '{step.name}' to default pipeline in "
            f"'bitbucket-pipelines.yml' because it is an import pipeline."
        )
        raise UnexpectedImportPipelineError(msg) from None

    # Early exit if the step already exists in some sense
    for existing_step in existing_steps:
        if bitbucket_steps_are_equivalent(existing_step, step):
            return

    # Add the step to the default pipeline
    mgr = BitbucketPipelinesYAMLManager()
    doc = mgr.get()
    model = mgr.model_validate()
    model = _add_step_in_default_via_model(step, model=model, doc=doc)
    mgr.commit_model(model)

    # Remove the placeholder step if it already exists
    placeholder = _get_placeholder_step()
    if not bitbucket_steps_are_equivalent(placeholder, step):
        # Only remove the placeholder if it hasn't already been added.
        remove_bitbucket_step_from_default(placeholder)


def _add_step_in_default_via_model(
    step: Step, *, model: PipelinesConfiguration, doc: YAMLDocument
) -> PipelinesConfiguration:
    _add_step_caches_via_model(step, model=model)

    if step.name != _PLACEHOLDER_NAME:
        # We need to selectively choose to report at a higher level.
        # It's not always notable that the placeholder is being added.
        tick_print(
            f"Adding '{step.name}' to default pipeline in 'bitbucket-pipelines.yml'."
        )

    step = step.model_copy(deep=True)

    # Resolve any anchorized script items in the step
    step = _resolve_script_anchors(step, model=model, doc=doc)

    # If the step is unrecognized, it will go at the end.
    prerequisites: set[str] = set()

    # N.B. Currently, we are not accounting for parallelism, whereas all these steps
    # could be parallel potentially.
    # See https://github.com/usethis-python/usethis-python/issues/149
    minor_versions = get_supported_minor_python_versions()
    step_order = [
        "Run pre-commit",
        # For these tools, sync them with the pre-commit removal logic
        "Run pyproject-fmt",
        "Run Ruff",
        "Run Ruff Formatter",
        "Run deptry",
        "Run Import Linter",
        "Run Codespell",
        *[f"Test on {version.to_short_string()}" for version in minor_versions],
    ]
    for step_name in step_order:
        if step_name == step.name:
            break
        prerequisites.add(step_name)

    weld_result = usethis._pipeweld.func.Adder(
        pipeline=get_pipeweld_pipeline_from_default(model),
        step=get_pipeweld_step(step),
        prerequisites=prerequisites,
    ).add()
    for instruction in weld_result.instructions:
        apply_pipeweld_instruction_via_model(
            instruction=instruction, step_to_insert=step, model=model
        )

    # Restore script_items to a serializable form
    # We synchronized it to content's list for anchor detection, but the ruamel.yaml
    # objects can't be serialized by pydantic. Convert to plain strings.
    if model.definitions is not None and model.definitions.script_items is not None:
        model.definitions.script_items = [
            str(item) for item in model.definitions.script_items
        ]

    return model


def _resolve_script_anchors(
    step: Step, *, model: PipelinesConfiguration, doc: YAMLDocument
) -> Step:
    """Resolve script item anchors by adding definitions and replacing with references."""
    # Process each script item in the step
    for idx, script_item in enumerate(step.script.root):
        if isinstance(script_item, ScriptItemAnchor):
            # Get the names of the anchors which are already defined in the file
            defined_script_item_by_name = get_defined_script_items(model=model, doc=doc)

            # If our anchor doesn't have a definition yet, we need to add it
            if script_item.name not in defined_script_item_by_name:
                _add_script_item_definition(
                    script_item_name=script_item.name, model=model, doc=doc
                )
                # Refresh the defined items after adding
                defined_script_item_by_name = get_defined_script_items(
                    model=model, doc=doc
                )

            # Replace the anchor reference with the actual script content
            resolved_script_item = defined_script_item_by_name[script_item.name]
            step.script.root[idx] = resolved_script_item

    return step


def _add_script_item_definition(
    *,
    script_item_name: ScriptItemName,
    model: PipelinesConfiguration,
    doc: YAMLDocument,
) -> None:
    """Add a script item definition to the YAML file's definitions section.

    This function:
    1. Looks up the script item in _SCRIPT_ITEM_LOOKUP
    2. Ensures definitions.script_items exists in both model and doc.content
    3. Inserts the item at the correct position based on canonical order
    4. Synchronizes model.definitions.script_items with doc.content

    Args:
        script_item_name: The name of the script item anchor to add.
        model: The pipelines configuration model to update.
        doc: YAMLDocument to modify.

    Raises:
        NotImplementedError: If the script item name is not recognized.
    """
    try:
        resolved_script_item = _SCRIPT_ITEM_LOOKUP[script_item_name]
    except KeyError:
        msg = f"Unrecognized script item anchor: '{script_item_name}'."
        raise NotImplementedError(msg) from None

    # Ensure definitions.script_items exists in both model and doc.content
    content = cast("dict", doc.content)
    if "definitions" not in content:
        content["definitions"] = {}
        if model.definitions is None:
            model.definitions = Definitions()
    if "script_items" not in content["definitions"]:
        content["definitions"]["script_items"] = CommentedSeq()

    # ALWAYS synchronize model to point to content's list
    # This ensures model sees LiteralScalarString objects with anchors
    if model.definitions is not None:
        model.definitions.script_items = content["definitions"]["script_items"]

    # Insert script item in canonical order based on _SCRIPT_ITEM_LOOKUP
    insertion_index = _get_script_item_insertion_index(
        script_item_name=script_item_name,
        model=model,
    )
    content["definitions"]["script_items"].insert(insertion_index, resolved_script_item)

    # Update model to point to the modified content list
    if model.definitions is not None:
        model.definitions.script_items = content["definitions"]["script_items"]


def _get_script_item_insertion_index(
    *, script_item_name: ScriptItemName, model: PipelinesConfiguration
) -> int:
    """Get the correct insertion index for a script item to maintain canonical order."""
    # Check if we have existing script items in the model
    if model.definitions is None or model.definitions.script_items is None:
        return 0

    existing_script_items = model.definitions.script_items
    canonical_order = list(_SCRIPT_ITEM_LOOKUP.keys())

    for i, existing_item in enumerate(existing_script_items):
        existing_name = anchor_name_from_script_item(existing_item)
        if (
            existing_name is not None
            and existing_name in canonical_order
            and canonical_order.index(script_item_name)
            < canonical_order.index(existing_name)
        ):
            return i

    return len(existing_script_items)  # Default to end


def remove_bitbucket_step_from_default(step: Step) -> None:
    """Remove a step from the default pipeline in the Bitbucket Pipelines configuration.

    If the default pipeline does not exist, or the step is not found, nothing happens.
    """
    if not (usethis_config.cpd() / "bitbucket-pipelines.yml").exists():
        return

    if step.name == _PLACEHOLDER_NAME:
        pass  # We need to selectively choose to report at a higher level.
        # It's not always notable that the placeholder is being removed.
    else:
        tick_print(
            f"Removing '{step.name}' from default pipeline in 'bitbucket-pipelines.yml'."
        )

    mgr = BitbucketPipelinesYAMLManager()
    doc = mgr.get()
    model = mgr.model_validate()

    if model.pipelines is None:
        return

    if model.pipelines.default is None:
        return

    pipeline = model.pipelines.default

    if isinstance(pipeline.root, ImportPipeline):
        msg = "Cannot remove steps from an import pipeline."
        raise UnexpectedImportPipelineError(msg)

    items = pipeline.root.root

    # Iterate over the items. Any item that contains the step is censored to remove
    # references to the step. If the only thing in the item is the step, we get None
    new_items: list[StepItem | ParallelItem | StageItem] = []
    for item in items:
        new_item = _censor_step(item, step=step)
        if new_item is not None:
            new_items.append(new_item)
    pipeline.root.root = new_items

    if len(new_items) == 0:
        placeholder = _get_placeholder_step()
        model = _add_step_in_default_via_model(placeholder, model=model, doc=doc)

    mgr.commit_model(model)

    if step.caches is not None:
        for cache in step.caches:
            if not is_cache_used(cache):
                remove_cache(cache)


@singledispatch
def _censor_step(
    item: StepItem | ParallelItem | StageItem, *, step: Step
) -> StepItem | ParallelItem | StageItem | None:
    """Censor a step from a pipeline item, with None if necessary."""
    raise NotImplementedError


@_censor_step.register(StepItem)
def _(item: StepItem, *, step: Step) -> StepItem | ParallelItem | StageItem | None:
    if bitbucket_steps_are_equivalent(item.step, step):
        return None
    return item


@_censor_step.register(ParallelItem)
def _(item: ParallelItem, *, step: Step) -> StepItem | ParallelItem | StageItem | None:
    par = item.parallel.root

    if isinstance(par, ParallelSteps):
        step_items = par.root
    elif isinstance(par, ParallelExpanded):
        step_items = par.steps.root
    else:
        assert_never(par)

    new_step_items: list[StepItem] = []
    for step_item in step_items:
        if bitbucket_steps_are_equivalent(step_item.step, step):
            continue
        new_step_items.append(step_item)

    if len(new_step_items) == 0:
        return None
    elif len(new_step_items) == 1 and len(step_items) != 1:
        return new_step_items[0]
    elif isinstance(par, ParallelSteps):
        return ParallelItem(parallel=Parallel(ParallelSteps(new_step_items)))
    elif isinstance(par, ParallelExpanded):
        par.steps = ParallelSteps(new_step_items)
        return ParallelItem(parallel=Parallel(par))
    else:
        assert_never(par)


@_censor_step.register(StageItem)
def _(item: StageItem, *, step: Step) -> StepItem | ParallelItem | StageItem | None:
    step1s = item.stage.steps

    new_step1s = []
    for step1 in step1s:
        if bitbucket_steps_are_equivalent(step1tostep(step1), step):
            continue
        new_step1s.append(step1)

    if len(new_step1s) == 0:
        return None

    new_stage = item.stage.model_copy()
    new_stage.steps = new_step1s
    return StageItem(stage=new_stage)


def is_cache_used(cache: str) -> bool:
    for step in get_steps_in_default():
        if step.caches is not None and cache in step.caches:
            return True

    return False


def _add_step_caches_via_model(step: Step, *, model: PipelinesConfiguration) -> None:
    if step.caches is not None:
        cache_by_name = {}
        for name in step.caches:
            try:
                cache = _CACHE_LOOKUP[name]
            except KeyError:
                msg = (
                    f"Unrecognized cache name '{name}' in step '{step.name}'. "
                    f"Supported caches are 'uv' and 'pre-commit'."
                )
                raise NotImplementedError(msg) from None
            cache_by_name[name] = cache
        _add_caches_via_model(cache_by_name, model=model)


def bitbucket_steps_are_equivalent(step1: Step | None, step2: Step) -> bool:
    if step1 is None:
        return False

    # Same name
    if step1.name == step2.name:
        return True

    # Same name up to case differences
    if (
        isinstance(step1.name, str)
        and isinstance(step2.name, str)
        and step1.name.lower() == step2.name.lower()
    ):
        return True

    # Same contents, different name
    step1 = step1.model_copy()
    step1.name = step2.name
    return step1 == step2


def get_steps_in_default() -> list[Step]:
    """Get the steps in the default pipeline of the Bitbucket Pipelines configuration.

    If the default pipeline does not exist, an empty list is returned.

    Returns:
        The steps in the default pipeline.

    Raises:
        UnexpectedImportPipelineError: If the pipeline is an import pipeline.
    """
    if not (usethis_config.cpd() / "bitbucket-pipelines.yml").exists():
        return []

    mgr = BitbucketPipelinesYAMLManager()
    model = mgr.model_validate()

    if model.pipelines is None:
        return []

    if model.pipelines.default is None:
        return []

    pipeline = model.pipelines.default

    return _get_steps_in_pipeline(pipeline)


def _get_steps_in_pipeline(pipeline: Pipeline) -> list[Step]:
    if isinstance(pipeline.root, ImportPipeline):
        msg = "Cannot retrieve steps from an import pipeline."
        raise UnexpectedImportPipelineError(msg)

    items = pipeline.root.root

    steps = []
    for item in items:
        steps.extend(get_steps_in_pipeline_item(item))

    return steps


@singledispatch
def get_steps_in_pipeline_item(item) -> list[Step]:
    raise NotImplementedError


@get_steps_in_pipeline_item.register(StepItem)
def _(item: StepItem) -> list[Step]:
    return [item.step]


@get_steps_in_pipeline_item.register(ParallelItem)
def _(item: ParallelItem) -> list[Step]:
    _p = item.parallel.root
    if isinstance(_p, ParallelSteps):
        step_items = _p.root
    elif isinstance(_p, ParallelExpanded):
        step_items = _p.steps.root
    else:
        assert_never(_p)

    steps = [step_item.step for step_item in step_items if step_item.step is not None]
    return steps


@get_steps_in_pipeline_item.register(StageItem)
def _(item: StageItem) -> list[Step]:
    return [step1tostep(step1) for step1 in item.stage.steps if step1.step is not None]


def add_placeholder_step_in_default(report_placeholder: bool = True) -> None:
    add_bitbucket_step_in_default(_get_placeholder_step())

    if report_placeholder:
        tick_print(
            "Adding placeholder step to default pipeline in 'bitbucket-pipelines.yml'."
        )
        instruct_print(
            "Remove the placeholder pipeline step in 'bitbucket-pipelines.yml'."
        )
        instruct_print("Replace it with your own pipeline steps.")
        instruct_print(
            "Alternatively, use 'usethis tool' to add other tools and their steps."
        )


def _get_placeholder_step() -> Step:
    backend = get_backend()

    if backend is BackendEnum.uv:
        return Step(
            name=_PLACEHOLDER_NAME,
            script=Script(
                [
                    ScriptItemAnchor(name="install-uv"),
                    "echo 'Hello, world!'",
                ]
            ),
            caches=["uv"],
        )
    elif backend is BackendEnum.none:
        return Step(
            name=_PLACEHOLDER_NAME,
            script=Script(
                [
                    "echo 'Hello, world!'",
                ]
            ),
        )
    else:
        assert_never(backend)


def get_defined_script_items(
    *, model: PipelinesConfiguration, doc: YAMLDocument
) -> dict[str, str]:
    """Get defined script items with their anchor names.

    Args:
        model: The pipelines configuration model.
        doc: YAMLDocument for accessing raw content with anchor information.
    """
    if model.definitions is None or model.definitions.script_items is None:
        return {}

    content = cast("dict", doc.content)
    if "definitions" not in content or "script_items" not in content["definitions"]:
        return {}

    script_item_contents = content["definitions"]["script_items"]

    script_anchor_by_name = {}
    for script_item_content in script_item_contents:
        if not isinstance(script_item_content, LiteralScalarString):
            # Not a script item definition
            continue

        anchor: Anchor = script_item_content.yaml_anchor()

        if anchor is None:
            # Unnamed definition, can't be used as an anchor
            continue

        anchor_name = anchor.value
        script_anchor_by_name[anchor_name] = script_item_content

    return script_anchor_by_name
