from pathlib import Path

from usethis._console import box_print, info_print
from usethis._integrations.bitbucket.anchor import ScriptItemAnchor
from usethis._integrations.bitbucket.config import (
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._integrations.bitbucket.steps import add_step_in_default
from usethis._integrations.pyproject.requires_python import (
    get_supported_major_python_versions,
)
from usethis._tool import PreCommitTool, PytestTool


def use_ci_bitbucket(*, remove: bool = False) -> None:
    if not remove:
        if (Path.cwd() / "bitbucket-pipelines.yml").exists():
            # Early exit; the file already exists so we will leave it alone.
            return

        add_bitbucket_pipeline_config()

        steps = []
        if PreCommitTool().is_used():
            add_step_in_default(
                Step(
                    name="Run pre-commit hooks",
                    caches=["uv", "pre-commit"],
                    script=Script(
                        [
                            ScriptItemAnchor(name="install-uv"),
                            "uv run pre-commit run --all-files",
                        ]
                    ),
                ),
            )
        if PytestTool().is_used():
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

        if not steps:
            # Add a dummy step
            add_step_in_default(
                Step(
                    name="Placeholder - add your own steps!",
                    caches=["uv"],
                    script=Script(
                        [
                            ScriptItemAnchor(name="install-uv"),
                            "echo 'Hello, world!'",
                        ]
                    ),
                ),
            )

            box_print("Populate the placeholder step in 'bitbucket-pipelines.yml'.")
            info_print(
                "Consider `usethis tool pytest` to start testing your code, including in the pipeline."
            )

        box_print("Run your first pipeline on the Bitbucket website.")
    else:
        remove_bitbucket_pipeline_config()
