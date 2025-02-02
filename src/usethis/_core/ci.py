from usethis._ci import (
    get_bitbucket_deptry_step,
    get_bitbucket_pre_commit_step,
    get_bitbucket_pyproject_fmt_step,
    get_bitbucket_ruff_step,
    update_bitbucket_pytest_steps,
)
from usethis._console import box_print, info_print
from usethis._integrations.bitbucket.config import (
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._integrations.bitbucket.steps import add_bitbucket_step_in_default
from usethis._integrations.uv.init import ensure_pyproject_toml
from usethis._tool import (
    DeptryTool,
    PreCommitTool,
    PyprojectFmtTool,
    PytestTool,
    RuffTool,
)


def use_ci_bitbucket(*, remove: bool = False) -> None:
    ensure_pyproject_toml()

    if not remove:
        use_pre_commit = PreCommitTool().is_used()
        use_pytest = PytestTool().is_used()
        use_ruff = RuffTool().is_used()
        use_deptry = DeptryTool().is_used()
        use_pyproject_fmt = PyprojectFmtTool().is_used()
        use_any_tool = (
            use_pre_commit or use_pytest or use_ruff or use_deptry or use_pyproject_fmt
        )

        add_bitbucket_pipeline_config(report_placeholder=not use_any_tool)

        if use_pre_commit:
            add_bitbucket_step_in_default(get_bitbucket_pre_commit_step())
        else:
            # This order should match the canonical order in the function which add
            # steps
            if use_pyproject_fmt:
                add_bitbucket_step_in_default(get_bitbucket_pyproject_fmt_step())
            if use_ruff:
                add_bitbucket_step_in_default(get_bitbucket_ruff_step())
            if use_deptry:
                add_bitbucket_step_in_default(get_bitbucket_deptry_step())

        if use_pytest:
            update_bitbucket_pytest_steps()

        else:
            info_print(
                "Consider `usethis tool pytest` to test your code for the pipeline."
            )

        box_print("Run your pipeline via the Bitbucket website.")
    else:
        remove_bitbucket_pipeline_config()
