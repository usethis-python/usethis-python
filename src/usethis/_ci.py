import re
from pathlib import Path

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


def update_bitbucket_pytest_steps() -> None:
    matrix = get_supported_major_python_versions()
    for version in matrix:
        add_step_in_default(
            Step(
                name=f"Test on 3.{version}",
                caches=["uv"],
                script=Script(
                    [
                        ScriptItemAnchor(name="install-uv"),
                        f"uv run --python 3.{version} pytest -x --junitxml=test-reports/report.xml",
                    ]
                ),
            ),
        )
    # We also need to remove any old steps that are not in the matrix
    for step in get_steps_in_default():
        if step.name is not None:
            match = re.match(r"^Test on 3\.(\d+)$", step.name)
            if match:
                version = int(match.group(1))
                if version not in matrix:
                    remove_step_from_default(step)


def remove_bitbucket_pytest_steps() -> None:
    # Remove any with pattern "^Test on 3.\d+$"
    for step in get_steps_in_default():
        if step.name is not None and re.match(r"^Test on 3.\d+$", step.name):
            remove_step_from_default(step)
