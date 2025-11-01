from __future__ import annotations

from usethis._console import how_print, info_print
from usethis._integrations.ci.bitbucket.config import (
    add_bitbucket_pipelines_config,
    remove_bitbucket_pipelines_config,
)
from usethis._tool.impl.codespell import CodespellTool
from usethis._tool.impl.deptry import DeptryTool
from usethis._tool.impl.import_linter import ImportLinterTool
from usethis._tool.impl.pre_commit import PreCommitTool
from usethis._tool.impl.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.pytest import PytestTool
from usethis._tool.impl.ruff import RuffTool


def use_ci_bitbucket(*, remove: bool = False, how: bool = False) -> None:
    if how:
        print_how_to_use_ci_bitbucket()
        return

    if not remove:
        use_pre_commit = PreCommitTool().is_used()
        use_pytest = PytestTool().is_used()
        use_ruff = RuffTool().is_used()
        use_deptry = DeptryTool().is_used()
        use_import_linter = ImportLinterTool().is_used()
        use_pyproject_fmt = PyprojectFmtTool().is_used()
        use_codespell = CodespellTool().is_used()
        use_any_tool = (
            use_pre_commit
            or use_pytest
            or use_ruff
            or use_deptry
            or use_import_linter
            or use_pyproject_fmt
            or use_codespell
        )

        add_bitbucket_pipelines_config(report_placeholder=not use_any_tool)

        if use_pre_commit:
            PreCommitTool().update_bitbucket_steps()
        else:
            # This order should match the canonical order in the function which adds
            # steps
            PyprojectFmtTool().update_bitbucket_steps()
            RuffTool().update_bitbucket_steps()
            DeptryTool().update_bitbucket_steps()
            ImportLinterTool().update_bitbucket_steps()
            CodespellTool().update_bitbucket_steps()

        PytestTool().update_bitbucket_steps()

        print_how_to_use_ci_bitbucket()
    else:
        remove_bitbucket_pipelines_config()


def print_how_to_use_ci_bitbucket() -> None:
    """Print how to use the Bitbucket CI service."""
    if not PytestTool().is_used():
        info_print("Consider `usethis tool pytest` to test your code for the pipeline.")

    how_print("Run your pipeline via the Bitbucket website.")
