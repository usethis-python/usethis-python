from functools import singledispatch
from pathlib import Path
from typing import assert_never

from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.scalarstring import LiteralScalarString

from usethis._config import usethis_config
from usethis._integrations.bitbucket.cache import add_caches
from usethis._integrations.bitbucket.dump import bitbucket_fancy_dump
from usethis._integrations.bitbucket.io import (
    edit_bitbucket_pipelines_yaml,
)
from usethis._integrations.bitbucket.schema import (
    CachePath,
    Definitions,
    ImportPipeline,
    Items,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Pipeline,
    Pipelines,
    Script,
    StageItem,
    Step,
    Step1,
    StepItem,
)
from usethis._integrations.yaml.update import update_ruamel_yaml_map

_ANCHOR_PREFIX = "usethis-anchor-"


class UnexpectedImportPipelineError(Exception):
    """Raised when an import pipeline is unexpectedly encountered."""


_CACHE_LOOKUP = {
    "uv": CachePath("~/.cache/uv"),
    "pre-commit": CachePath("~/.cache/pre-commit"),
}

# TODO can we just set the anchor in here somehow and then share?
_SCRIPT_ITEM_LOOKUP: dict[str, LiteralScalarString] = {
    "install-uv": LiteralScalarString("""\
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
export UV_LINK_MODE=copy
uv --version
""")
}


# TODO reduce the complexity of the below function and enable the ruff rule
def add_step_in_default(step: Step) -> None:  # noqa: PLR0912
    # TODO need to explain that script items which start with the prefix "usethis-anchor-"
    # get the anchor imputed
    # TODO we can handle it with caches, where we hard-code some anchors which
    # we plan to know about, and add them if they are missing. This will let us use
    # *install-uv syntax instead of usethis-anchor-install-uv which is much clearer.
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
        if _steps_are_equivalent(existing_step, step):
            return

    add_step_caches(step)

    # Add the step to the default pipeline
    with edit_bitbucket_pipelines_yaml() as doc:
        step = step.model_copy(deep=True)

        for idx, script_item in enumerate(step.script.root):
            if isinstance(script_item, str) and script_item.startswith(_ANCHOR_PREFIX):
                name = script_item.removeprefix(_ANCHOR_PREFIX)
                try:
                    script_item = _SCRIPT_ITEM_LOOKUP[name]
                except KeyError:
                    pass
                else:
                    # TODO shouldn't add this if it already exists - need to test this case
                    config = doc.model

                    if config.definitions is None:
                        config.definitions = Definitions()

                    script_items = config.definitions.script_items

                    if script_items is None:
                        script_items = CommentedSeq()
                        config.definitions.script_items = script_items

                    # N.B. when we add the definition, we are relying on this being an append
                    # (and below return statement)
                    # TODO revisit this - maybe we should add alphabetically.
                    script_items.append(script_item)
                    script_items = CommentedSeq(script_items)

                    # Add an anchor.
                    script_item.yaml_set_anchor(value=name, always_dump=True)
                    step.script.root[idx] = script_item

        # TODO currently adding to the end, but need to test desired functionality
        # of adding after a specific step
        if doc.model.pipelines is None:
            doc.model.pipelines = Pipelines()

        pipelines = doc.model.pipelines
        default = pipelines.default

        if default is None:
            items = []
        elif isinstance(default.root, ImportPipeline):
            msg = (
                f"Cannot add step '{step.name}' to default pipeline in "
                f"'bitbucket-pipelines.yml' because it is an import pipeline."
            )
            raise UnexpectedImportPipelineError(msg)
        else:
            items = default.root.root

        items.append(StepItem(step=step))

        if default is None:
            pipelines.default = Pipeline(Items(items))

        dump = bitbucket_fancy_dump(doc.model, reference=doc.content)

        update_ruamel_yaml_map(
            doc.content,
            dump,
            preserve_comments=True,
        )

    # TODO need to tell the user to review the pipeline, it might be wrong. Test
    # associated message.


def add_step_caches(step: Step) -> None:
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
        add_caches(cache_by_name)


def _steps_are_equivalent(step1: Step, step2: Step) -> bool:
    # Same name
    if step1.name == step2.name:
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
    if not (Path.cwd() / "bitbucket-pipelines.yml").exists():
        return []

    with edit_bitbucket_pipelines_yaml() as doc:
        config = doc.model

    if config.pipelines is None:
        return []

    if config.pipelines.default is None:
        return []

    pipeline = config.pipelines.default

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
def get_steps_in_pipeline_item(item) -> list[Step]: ...


@get_steps_in_pipeline_item.register(StepItem)
def _(item: StepItem) -> list[Step]:
    if item.step is None:
        return []

    return [item.step]


@get_steps_in_pipeline_item.register(ParallelItem)
def _(item: ParallelItem) -> list[Step]:
    if item.parallel is None:
        return []

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
    if item.stage is None:
        return []

    step1s = item.stage.steps

    steps = [_step1tostep(step1) for step1 in step1s if step1.step is not None]

    return steps


def _step1tostep(step1: Step1) -> Step:
    """Promoting Step1 to a standard Step.

    This is necessary because there is some unusual inconsistency in the JSON Schema
    for Bitbucket pipelines that means conditions are not constrained by type when
    occurring in a stage, whereas at time of writing they are constrained in all other
    circumstances. This gives rise to strange naming in the output of
    datamodel-code-generator (which is repeated here for consistency).
    """
    if step1.step is None:
        msg = (
            "When parsing Bitbucket pipelines, expected each step of a stage to itself "
            "have a non-null step, but got null."
        )
        raise ValueError(msg)

    step2 = step1.step

    step = Step(**step2.model_dump())
    return step


def add_placeholder_step_in_default() -> None:
    # TODO message and test?
    with usethis_config.set(quiet=True):
        add_step_in_default(_get_placeholder_step())


def _get_placeholder_step() -> Step:
    return Step(
        name="Placeholder - add your own steps!",
        # TODO maybe instead of doing anchors with this string-prefix thing, we can
        # use * as a symbol, which presumably would be invalid in a script so fine in
        # this context. Need to learn more about this.
        script=Script(
            [
                "usethis-anchor-install-uv",
                "echo 'Hello, world!'",
            ]
        ),
        caches=["uv"],
    )
