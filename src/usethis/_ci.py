import re
from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.bitbucket.anchor import ScriptItemAnchor
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._integrations.bitbucket.steps import (
    add_step_in_default,
    get_steps_in_default,
    remove_step_from_default,
)
from usethis._integrations.uv.python import get_supported_major_python_versions


def is_bitbucket_used() -> bool:
    return (Path.cwd() / "bitbucket-pipelines.yml").exists()


def add_bitbucket_pre_commit_step() -> None:
    add_step_in_default(_get_bitbucket_pre_commit_step())


def remove_bitbucket_pre_commit_step() -> None:
    tick_print("Removing pre-commit step from 'bitbucket-pipelines.yml'.")
    remove_step_from_default(_get_bitbucket_pre_commit_step())


def _get_bitbucket_pre_commit_step() -> Step:
    return Step(
        name="Run pre-commit",
        caches=["uv", "pre-commit"],
        script=Script(
            [
                ScriptItemAnchor(name="install-uv"),
                "uv run pre-commit run --all-files",
            ]
        ),
    )


def add_bitbucket_pytest_steps() -> None:
    matrix = get_supported_major_python_versions()
    for version in matrix:
        add_step_in_default(
            Step(
                name=f"Test - Python 3.{version}",
                caches=["uv"],
                script=Script(
                    [
                        ScriptItemAnchor(name="install-uv"),
                        f"uv run --python 3.{version} pytest",
                    ]
                ),
            ),
        )


def remove_bitbucket_pytest_steps() -> None:
    tick_print("Removing pytest steps from 'bitbucket-pipelines.yml'.")
    # Remove any with pattern "^Test - Python 3.\d+$"
    for step in get_steps_in_default():
        if step.name is not None and re.match(r"^Test - Python 3.\d+$", step.name):
            remove_step_from_default(step)
