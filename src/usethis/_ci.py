from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.bitbucket.anchor import ScriptItemAnchor
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._integrations.bitbucket.steps import (
    add_step_in_default,
    remove_step_from_default,
)
from usethis._integrations.pyproject.requires_python import (
    get_supported_major_python_versions,
)


def is_bitbucket_used() -> bool:
    return (Path.cwd() / "bitbucket-pipelines.yml").exists()


def add_bitbucket_precommit_step() -> None:
    tick_print("Adding pre-commit step to 'bitbucket-pipelines.yml'.")
    add_step_in_default(_get_bitbucket_precommit_step())


def remove_bitbucket_precommit_step() -> None:
    tick_print("Removing pre-commit step from 'bitbucket-pipelines.yml'.")
    remove_step_from_default(_get_bitbucket_precommit_step())


def _get_bitbucket_precommit_step() -> Step:
    return Step(
        # TODO need some way of syncing this name with the name in steps.py
        # Perhaps this function should live in there really? See what we do for the
        # equivalent when adding pre-commit hooks. Where do the hook implementations
        # live? Perhaps they merit their own module.
        name="Run pre-commit hooks",
        caches=["uv", "pre-commit"],
        script=Script(
            [
                ScriptItemAnchor(name="install-uv"),
                "uv run pre-commit run --all-files",
            ]
        ),
    )


def add_bitbucket_pytest_steps() -> None:
    tick_print("Adding pytest matrix steps to 'bitbucket-pipelines.yml'.")
    matrix = get_supported_major_python_versions()
    for version in matrix:
        add_step_in_default(
            Step(
                name=f"Run tests with Python 3.{version}",
                caches=["uv"],
                script=Script(
                    [
                        ScriptItemAnchor(name="install-uv"),
                        f"uv run --python 3.{version} pytest",
                    ]
                ),
            ),
        )
