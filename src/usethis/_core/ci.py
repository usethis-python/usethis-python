from __future__ import annotations

from usethis._console import how_print, info_print
from usethis._integrations.ci.bitbucket.config import (
    add_bitbucket_pipelines_config,
    remove_bitbucket_pipelines_config,
)
from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.pytest import PytestTool


def use_ci_bitbucket(
    *, remove: bool = False, how: bool = False, matrix_python: bool = True
) -> None:
    if how:
        print_how_to_use_ci_bitbucket()
        return

    if not remove:
        use_any_tool = PytestTool().is_used() or any(
            tool.is_used() for tool in ALL_TOOLS
        )

        add_bitbucket_pipelines_config(report_placeholder=not use_any_tool)

        for tool in ALL_TOOLS:
            tool.update_bitbucket_steps()

        PytestTool().update_bitbucket_steps(matrix_python=matrix_python)

        print_how_to_use_ci_bitbucket()
    else:
        remove_bitbucket_pipelines_config()


def print_how_to_use_ci_bitbucket() -> None:
    """Print how to use the Bitbucket CI service."""
    _suggest_pytest()

    how_print("Run your pipeline via the Bitbucket website.")


def _suggest_pytest() -> None:
    if not PytestTool().is_used():
        info_print("Consider `usethis tool pytest` to test your code for the pipeline.")
