from pathlib import Path

from usethis._console import box_print, info_print
from usethis._integrations.bitbucket.anchor import ScriptItemAnchor
from usethis._integrations.bitbucket.config import (
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._integrations.bitbucket.steps import (
    add_placeholder_step_in_default,
    add_step_in_default,
)
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
        # TODO need integration in the other direction (and to test it) - if we run
        # usethis tool pre-commit and then usethis ci bitbucket, we should get the
        # pre-commit step in the pipeline
        # Also need a mechanism for removals if we run usethis tool pre-commit --remove
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
            add_placeholder_step_in_default()
            info_print(
                "Consider `usethis tool pytest` to start testing your code, including in the pipeline."
            )

        box_print("Run your first pipeline on the Bitbucket website.")
    else:
        remove_bitbucket_pipeline_config()
