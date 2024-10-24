from pathlib import Path
from typing import Any, Literal, assert_never

from pydantic import BaseModel

from usethis._integrations.bitbucket.cache import Cache, add_cache
from usethis._utils._yaml import edit_yaml


class StepRef(BaseModel):
    """The reference to pre-defined step."""

    name: Literal["install-uv"]


class Step(BaseModel):
    name: str
    caches: list[Literal["uv", "pre-commit"]]
    script: list[StepRef | str]


def add_steps(
    steps: list[Step], *, is_parallel: bool, pipeline: str = "default"
) -> None:
    """Add new steps to a Bitbucket Pipelines config.

    The steps are placed at the end, after any existing configuration, but joining
    any existing parallelism if possible and applicable.

    Args:
        steps: The steps to add.
        is_parallel: Whether the steps should be parallel.
        pipeline: The pipeline to add the steps to. Default is "default".
    """

    # Insert any relevant caches
    for step in steps:
        _add_relevant_caches(step)

    path = Path.cwd() / "bitbucket-pipelines.yml"

    with edit_yaml(path) as content:
        # Get all the pre-defined scripts as anchors
        try:
            raw_scripts = content["definitions"]["scripts"]
        except KeyError:
            raw_scripts = []

        scripts = {
            raw_script["script"].anchor.value: raw_script["script"]
            for raw_script in raw_scripts
        }

        # Rework the current steps
        new_step_dicts = []
        for step in steps:
            sd = {}
            sd["name"] = step.name
            # Only include cache list if non-empty
            if step.caches:
                sd["caches"] = step.caches

            sd["script"] = [
                s if not isinstance(s, StepRef) else scripts[s.name]
                for s in step.script
            ]

            new_step_dicts.append({"step": sd})

        # Get the steps
        current_steps: list[Any] = content["pipelines"][pipeline]

        # Add the new steps
        if not is_parallel:
            current_steps.extend(new_step_dicts)
        elif not current_steps or "parallel" not in current_steps[-1]:
            if len(new_step_dicts) == 1:
                current_steps.extend(new_step_dicts)
            else:
                current_steps.append({"parallel": new_step_dicts})
        else:
            current_steps[-1]["parallel"].extend(new_step_dicts)


def _add_relevant_caches(step: Step) -> None:
    for cache in step.caches:
        if cache == "uv":
            add_cache(
                Cache(name="uv", path="~/.cache/uv"),
                exists_ok=True,
            )
        elif cache == "pre-commit":
            add_cache(
                Cache(name="pre-commit", path="~/.cache/pre-commit"),
                exists_ok=True,
            )
        else:
            assert_never(cache)
