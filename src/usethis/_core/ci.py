from usethis._ci import update_bitbucket_pytest_steps
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


def _add_optional_bitbucket_steps(
    use_pyproject_fmt: bool, use_ruff: bool, use_deptry: bool
) -> None:
    if use_pyproject_fmt:
        step = PyprojectFmtTool().get_bitbucket_step()
        if step:
            add_bitbucket_step_in_default(step)
    if use_ruff:
        step = RuffTool().get_bitbucket_step()
        if step:
            add_bitbucket_step_in_default(step)
    if use_deptry:
        step = DeptryTool().get_bitbucket_step()
        if step:
            add_bitbucket_step_in_default(step)


def use_ci_bitbucket(*, remove: bool = False) -> None:
    ensure_pyproject_toml()
    if remove:
        remove_bitbucket_pipeline_config()
        return  # Early return to reduce branch depth

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
        step = PreCommitTool().get_bitbucket_step()
        if step:
            add_bitbucket_step_in_default(step)
    else:
        _add_optional_bitbucket_steps(use_pyproject_fmt, use_ruff, use_deptry)

    if use_pytest:
        update_bitbucket_pytest_steps()
    else:
        info_print("Consider `usethis tool pytest` to test your code for the pipeline.")

    box_print("Run your pipeline via the Bitbucket website.")
