from __future__ import annotations

from usethis._console import how_print, info_print
from usethis._integrations.ci.bitbucket.config import (
    add_bitbucket_pipelines_config,
    remove_bitbucket_pipelines_config,
)
from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.codespell import CodespellTool
from usethis._tool.impl.deptry import DeptryTool
from usethis._tool.impl.import_linter import ImportLinterTool
from usethis._tool.impl.pre_commit import PreCommitTool
from usethis._tool.impl.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.pytest import PytestTool
from usethis._tool.impl.ruff import RuffTool

# Ordered list of QA tools that should run in CI (matches canonical step order)
# These tools run via pre-commit if available, otherwise directly in CI
_CI_QA_TOOL_TYPES = [
    PreCommitTool,
    PyprojectFmtTool,
    RuffTool,
    DeptryTool,
    ImportLinterTool,
    CodespellTool,
]


def use_ci_bitbucket(
    *, remove: bool = False, how: bool = False, matrix_python: bool = True
) -> None:
    if how:
        print_how_to_use_ci_bitbucket()
        return

    if not remove:
        use_any_tool = any(tool.is_used() for tool in ALL_TOOLS)

        add_bitbucket_pipelines_config(report_placeholder=not use_any_tool)

        # Add steps for QA tools in canonical order
        for tool_type in _CI_QA_TOOL_TYPES:
            # Find the matching tool instance in ALL_TOOLS
            for tool in ALL_TOOLS:
                if isinstance(tool, tool_type):
                    tool.update_bitbucket_steps()
                    break

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
