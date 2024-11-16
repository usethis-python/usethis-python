from functools import singledispatch
from typing import assert_never

from ruamel.yaml.comments import CommentedMap

from usethis._integrations.bitbucket.cache import add_caches
from usethis._integrations.bitbucket.dump import fancy_pipelines_model_dump
from usethis._integrations.bitbucket.io import (
    edit_bitbucket_pipelines_yaml,
    read_bitbucket_pipelines_yaml,
)
from usethis._integrations.bitbucket.pipeline import (
    CachePath,
    ImportPipeline,
    Items,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Pipe,
    Pipeline,
    Pipelines,
    StageItem,
    Step,
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


def add_step_in_default(
    step: Step, *, script_item_by_name: dict[str, str | Pipe] | None = None
) -> None:
    # TODO need to explain that script items which start with the prefix "usethis-anchor-"
    # get the dict value imputed as an anchor
    if script_item_by_name is None:
        script_item_by_name = {}

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
    anchorize_script_refs(step, script_item_by_name=script_item_by_name)

    # Add the step to the default pipeline
    with edit_bitbucket_pipelines_yaml() as doc:
        # TODO this validation might be better shared across all uses of the context
        # manager. On the other hand, what we're doing here is really "lazy" validation
        # and if there is no other case where we _need_ to do this validation then
        # maybe it's not worth it.
        if not isinstance(doc.content, CommentedMap):
            msg = (
                f"Error when parsing Bitbucket Pipelines configuration. Expected file "
                f"to be a map, got {type(doc.content)}."
            )
            raise ValueError(msg)

        # TODO currently adding to the end, but need to test desired functionality
        # of adding after a specific step
        pipelines = doc.model.pipelines

        if pipelines is None:
            pipelines = Pipelines()

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

        items.append(StepItem(step=step.model_copy()))

        if default is None:
            pipelines.default = Pipeline(Items(items))

        dump = fancy_pipelines_model_dump(doc.model, reference=doc.content)

        update_ruamel_yaml_map(
            doc.content,
            dump,
            preserve_comments=True,
        )

    # TODO need to tell the user to review the pipeline, it might be wrong.


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


def anchorize_script_refs(
    step: Step, *, script_item_by_name: dict[str, str | Pipe]
) -> Step:
    step = step.model_copy(deep=True)

    for idx, script_item in enumerate(step.script):
        if isinstance(script_item, str) and script_item.startswith(_ANCHOR_PREFIX):
            name = script_item.removeprefix(_ANCHOR_PREFIX)
            try:
                # TODO this line needs testing big-time - it had a bug but wasn't
                # caught until doing refactoring!
                script_item = script_item_by_name[name]
            except KeyError:
                pass
            else:
                # TODO test this branch of the if-statement.
                step.script.root[idx] = script_item

    return step


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
    config = read_bitbucket_pipelines_yaml()

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
        steps.extend(_get_steps_in_pipeline_item(item))

    return steps


@singledispatch
def _get_steps_in_pipeline_item(item) -> list[Step]: ...


@_get_steps_in_pipeline_item.register(StepItem)
def _(item: StepItem) -> list[Step]:
    if item.step is None:
        return []

    return [item.step]


@_get_steps_in_pipeline_item.register(ParallelItem)
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

    steps = []
    for step_item in step_items:
        if step_item.step is None:
            continue

        steps.append(step_item.step)
    return steps


@_get_steps_in_pipeline_item.register(StageItem)
def _(item: StageItem) -> list[Step]:
    if item.stage is None:
        return []

    step1s = item.stage.steps

    # Some unusual inconsistency in the JSON Schema for Bitbucket pipelines
    # means that conditions are not constrained by type when occurring in a
    # stage, whereas at time of writing they are constrained in all other
    # circumstances. This gives rise to strange naming in the output of
    # datamodel-code-generator (which is repeated here for consistency).
    steps = []
    for step1 in step1s:
        if step1.step is None:
            continue

        step2 = step1.step
        # Here, we are casting our Step2 to a standard step, which is fine
        # since one is the subtype of another
        # TODO should test this is actually the case.
        step = Step(**step2.model_dump())
        steps.append(step)
    return steps


# TODO Rather than using StepRef, let's encode the actual step, and refer via variable
# rather than string ref.
# This will allow us to do smarter things like autoamtically add an anchor if the step
# contents are the same.
# class StepRef(BaseModel):
#     """The reference to pre-defined step."""

#     name: Literal["install-uv"]


# # TODO can't we use the class from pipeline_schema?
# class Step(BaseModel):
#     name: str
#     caches: list[Literal["uv", "pre-commit"]]
#     script: list[StepRef | str]

# TODO commented out code
# # The canonical SPG for Bitbucket pipeline steps.
# # The idea is that each element in the outer list is in series, and each element in the
# # inner list is in parallel
# CANONICAL_SPG: list[list[str]] = [
#     [
#         "Placeholder - add your own steps!",
#         "Run pre-commit hooks",
#         *[
#             f"Run tests with Python 3.{v}" for v in range(0, 14)
#         ],  # TODO test this range is complete against the End of Life website
#     ],
# ]
# # Flat approach
# CANONICAL_STEPS: list[str] = [step for par_steps in CANONICAL_SPG for step in par_steps]


# def add_step_to_pipeline(step: Step, pipeline: Literal["default"]) -> None:
#     """Add a new step to a Bitbucket Pipelines config.

#     The step is placed using a heuristic which tries to put it at the most sensible
#     location in the pipeline. usethis has a notion of what the predecessors are for a
#     given step, and will try to insert the step as soon as possible after its
#     predecessors.

#     In general, this is not a safe operation since steps can have side effects when
#     running, so a general pipeline might break and a manual review of the pipeline
#     configuration is required. The user is notified of this.

#     If the only step so far is a usethis-created placeholder step, it is replaced by the
#     new step.

#     Args:
#         steps: The steps to add.
#         pipeline_name: The pipeline to add the steps to.
#     """
#     if _add_step_to_pipeline(step, pipeline):  # TODO yuck pass-through
#         _add_relevant_caches(step)


# # TODO this way of specifying default-only is misguided, string based arg won't do.
# # We should hard-code this or generalize it.
# def _add_step_to_pipeline(step: Step, pipeline: Literal["default"]) -> bool:
#     if pipeline != "default":
#         msg = f"Adding steps to pipeline '{pipeline}' not yet supported."
#         raise NotImplementedError(msg)

#     tick_print(
#         f"Adding step '{step.name}' to the '{pipeline}' pipeline in 'bitbucket-pipelines.yml'."
#     )

#     with edit_yaml(Path.cwd() / "bitbucket-pipelines.yml") as yaml_document:
#         content = yaml_document.content

#         m = PipelinesConfiguration.model_validate(yaml_document.content)

#         # Initialize sections we will always use - these will be createed if they
#         # don't exist

#         if m.pipelines is None:
#             m.pipelines = Pipelines(default=Pipeline([]))
#         elif m.pipelines.default is None:
#             m.pipelines.default = Pipeline([])

#         # Three steps to this process:
#         # 1. Get references to scripts defined in the definitions section
#         # 2. Construct the new steps in the format expected by ruamel.yaml
#         # 3. Insert the new steps into the pipeline

#         # #########################
#         # Step 1

#         # In the definitions section, we have scripts defined using &anchors for their
#         # names. We want to get a (Python) reference to the script, which will
#         # allow us to add the corresponding *alias to the script in the steps using
#         # ruamel.yaml.

#         # Technically, this step is only necessary if we use a script reference in the
#         # step.
#         # #########################

#         # See if there are any scripts defined
#         # TODO rather than doing a hard validation with errors, we could just rename the
#         # section to something else if it doesn't satisfy the expected name. Not sure
#         # what algorithm to use but perhaps could just increment; scripts1 etc.

#         if in_definitions:
#             raise NotImplementedError  # TODO

#         # #########################
#         # Step 2

#         # Construct the YAML-style object for the new step
#         # #########################
#         # Create the YAML-style dict for the step's properties
#         _s = {}

#         # Add the properties to the dict
#         _s["name"] = step.name
#         if step.caches:
#             _s["caches"] = step.caches
#         # We need to impute the actual script at the anchor over the script ref
#         # Alternatively, it might just be a pure script string
#         # TODO what if the s.name key is not in the script_maps_by_name?
#         _s["script"] = [
#             s if not isinstance(s, StepRef) else script_items_by_name[s.name]
#             for s in step.script
#         ]
#         step_map = {"step": _s}

#         # #########################
#         # Step 3

#         # Insert the new step into the pipeline
#         # #########################

#         # Finally, go through all the steps in the pipeline and ensure that the new
#         # step is not already present
#         for idx, _item in enumerate(pipelines[pipeline]):
#             try:
#                 _s = _item["step"]
#             except KeyError:
#                 # It's not a step, it's a parallel block
#                 try:
#                     _p = _item["parallel"]
#                 except KeyError:
#                     msg = f"Unrecognized pipeline item format: {_item}"
#                     raise NotImplementedError(msg)

#                 for _pitem in _p:
#                     try:
#                         _name = _pitem["step"]["name"]
#                     except KeyError:
#                         msg = f"Unrecognized pipeline item format in parallel block: {_pitem}"
#                         raise NotImplementedError(msg)
#                     if _name == step.name:
#                         # Step already exists.
#                         return False
#             else:
#                 if _s["name"] == step.name:
#                     # Step already exists.
#                     return False

#         # From this point on, we will definitely be adding the step.

#         # First, check if there is a single placeholder step; if so, remove it
#         if len(pipelines[pipeline]) == 1:
#             try:
#                 _s = pipelines[pipeline][0]["step"]
#             except KeyError:
#                 # It's not a step, it's a parallel block
#                 pass
#             else:
#                 if _s["name"] == "Placeholder - add your own steps!":
#                     pipelines[pipeline] = []

#         # Or, if there are no steps, again it's a simple case
#         if len(pipelines[pipeline]) == 0:
#             pipelines[pipeline] = [step_map]
#             return True

#         # Otherwise, we will insert the new step as soon as possible after its
#         # predecessors.

#         # Find its predecessors - look for the parallel block containing the step in
#         # the canonical SPG, and then all steps in previous parallel blocks are its
#         # predecessors.
#         predecessor_idx = None
#         for idx, par_steps in enumerate(CANONICAL_SPG):
#             if step.name in par_steps:
#                 predecessor_idx = idx
#                 break
#         if predecessor_idx is None:
#             msg = f"Step '{step.name}' not recognized."
#             raise NotImplementedError(msg)

#         if predecessor_idx == 0:
#             # No predecessors, so we're safe to insert at the start of the pipeline
#             pipelines[pipeline].insert(0, step_map)
#             return True

#         predecessors = [
#             _step
#             for _par_steps in CANONICAL_SPG[: predecessor_idx - 1]
#             for _step in _par_steps
#         ]
#         # Also interested in mates: steps that can be run in parallel with the new step
#         mates = []
#         predecessor_mates = []  # running in parallel so only a "cosmentic" predecessor
#         found_self = False
#         for _step in CANONICAL_SPG[predecessor_idx]:
#             if _step == step.name:
#                 found_self = True

#             mates.append(_step)
#             if not found_self:
#                 predecessor_mates.append(_step)

#         # Find the final predecessor in the pipeline, working backwards
#         # We'll insert the new step after this step
#         insert_idx = None
#         for idx, _item in reversed(list(enumerate(pipelines[pipeline]))):
#             try:
#                 _s = _item["step"]
#             except KeyError:
#                 # It's a parallel block;
#                 # we need to iterate over its steps to check each name individually.
#                 # If any of the names are in the predecessors, the whole parallel block
#                 # effectively gives the index of the predecessor.
#                 try:
#                     _p = _item["parallel"]
#                 except KeyError:
#                     msg = f"Unrecognized pipeline item format: {_item}"
#                     raise NotImplementedError(msg)

#                 for _pitem in _p:
#                     try:
#                         _name = _pitem["step"]["name"]
#                     except KeyError:
#                         msg = f"Unrecognized pipeline item format in parallel block: {_pitem}"
#                         raise NotImplementedError(msg)
#                     if _name in predecessors:
#                         insert_idx = idx
#                         break
#             else:
#                 if _s["name"] in predecessors:
#                     insert_idx = idx
#                     break

#         if insert_idx is None:
#             # No predecessors found in the pipeline, so we'll insert at the beginning
#             pipelines[pipeline].insert(0, step_map)
#             return True

#         # Insert after the last precedessor.
#         # If nothing exists after the predecessor, we'll insert at the end of the pipeline.
#         # We should form parallel blocks if possible; if the successor is a mate step,
#         # we'll combine the two together into a parallel block.
#         # If the successor is already a parallel block, we will check if _all_ of the
#         # steps in the parallel block are mates, among those occuring in the canonical
#         # SPG. If so, we will add the new step to the parallel block.
#         # Otherwise, the new step can be inserted standalone.
#         try:
#             _item = pipelines[pipeline][insert_idx + 1]
#         except IndexError:
#             # No successor, so we'll insert at the end and we're finished.
#             pipelines[pipeline].append(step_map)
#             return True

#         try:
#             _s = _item["step"]
#         except KeyError:
#             # It's a parallel block
#             try:
#                 _p = _item["parallel"]
#             except KeyError:
#                 msg = f"Unrecognized pipeline item format: {_item}"
#                 raise NotImplementedError(msg)

#             _p_idx = None
#             for idx, _pitem in enumerate(_p):
#                 try:
#                     _name = _item["step"]["name"]
#                 except KeyError:
#                     msg = (
#                         f"Unrecognized pipeline step format in parallel block: {_pitem}"
#                     )
#                     raise NotImplementedError(msg)

#                 if _name in CANONICAL_STEPS:
#                     if _name not in mates:
#                         # Not safe to combine with the parallel block, insert standalone
#                         pipelines[pipeline].insert(insert_idx + 1, step_map)
#                         return True
#                     else:
#                         # There is a mate, so as long as we don't find a non-mate and
#                         # return early we will be able to insert at this index.
#                         # It increases every iteration until it gets to the last mate
#                         _p_idx = idx

#             if _p_idx is None:
#                 # No mates found in the parallel block, so we insert standalone
#                 # TODO this whole if-statement was AI generated (!) so it needs to be
#                 # checked for correctness
#                 pipelines[pipeline].insert(insert_idx + 1, step_map)
#                 return True

#             # We've made it this far, so there are no non-mates; we are safe to insert
#             # the new step into the parallel block.
#             _p.insert(_p_idx + 1, step_map)
#         else:
#             if _s["name"] in predecessor_mates:
#                 # We can combine the new step with the existing step into a parallel
#                 # block
#                 pipelines[pipeline][insert_idx + 1] = {"parallel": [_item, step_map]}
#             elif _s["name"] in mates:
#                 pipelines[pipeline][insert_idx + 1] = {"parallel": [step_map, _item]}
#             else:
#                 # It's not a mate, so we insert the new step standalone
#                 pipelines[pipeline].insert(insert_idx + 1, step_map)

#         return True


# def _get_defined_step(*, config: PipelinesConfiguration, anchor_name: str) -> None:
#     # TODO ideally this function doesn't ever raise any errors and will do its best to
#     # recover

#     scripts_name = "scripts"
#     script_name = "script"
#     script_items: list[CommentedMap] = []
#     if config.definitions is not None:
#         try:
#             script_items_seq = config.definitions.__getattr__(scripts_name)
#         except AttributeError:
#             pass
#         else:
#             if not isinstance(script_items_seq, CommentedSeq):
#                 # TODO: is it better to raise, or to console print right here right now?
#                 msg = (
#                     f"Expected 'definitions.{scripts_name}' section to be an "
#                     f"array, got {type(script_items_seq)}."
#                 )
#                 raise ValueError(msg)

#             script_items = list(script_items_seq)

#             for idx, script_item in enumerate(script_items):
#                 if not isinstance(script_item, CommentedMap):
#                     msg = (
#                         f"Expected elements in 'definitions.{scripts_name}' to be "
#                         f"maps, got {type(script_item)} at index {idx}."
#                     )
#                     raise ValueError(msg)
#                 if script_name not in script_item:
#                     msg = (
#                         f"Expected elements in 'definitions.{scripts_name}' to be "
#                         f"maps with key '{script_name}', element at index {idx} is "
#                         f"missing this key."
#                     )
#                     raise ValueError(msg)

#     # Get the scripts indexed by their name (i.e. their anchor's name)
#     for script_item in script_items:
#         script = script_item[script_name]

#         # TODO all model_validate calls should be caught and consolified
#         Script.model_validate(script)

#         if not isinstance(script, CommentedSeq):
#             msg = (
#                 f"Expected '{script_name}' key in 'definitions.{scripts_name}' to "
#                 f"be an array, got {type(script_item[script_name])}."
#             )
#             raise ValueError(msg)

#         anchor: Anchor = script.anchor

#         if anchor is not None and anchor.value == anchor_name:
#             return script_item

#     # Anchor not found - we'll add it
#     # TODO rather than adding a new one, could check whether any existing steps have
#     # identical contents but just use a different anchor name or have no anchor, and
#     # then we could use that one. We could also move a step out of a pipeline and into
#     # the definitions section...

#     raise NotImplementedError  # TODO


# def _add_relevant_caches(step: Step) -> None:
#     for cache in step.caches:
#         if cache == "uv":
#             add_cache(
#                 Cache(name="uv", path="~/.cache/uv"),
#                 exists_ok=True,
#             )
#         elif cache == "pre-commit":
#             add_cache(
#                 Cache(name="pre-commit", path="~/.cache/pre-commit"),
#                 exists_ok=True,
#             )
#         else:
#             msg = (
#                 f"Unrecognized cache name '{cache}' in step '{step.name}'. "
#                 "Valid caches are 'uv' and 'pre-commit'."
#             )
#             raise NotImplementedError(msg)
