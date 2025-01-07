from usethis._ci import (
    add_bitbucket_pre_commit_step,
    add_bitbucket_pytest_steps,
    is_bitbucket_used,
    remove_bitbucket_pre_commit_step,
    remove_bitbucket_pytest_steps,
)
from usethis._console import box_print
from usethis._integrations.pre_commit.core import (
    # add_pre_commit_config_file,
    install_pre_commit_hooks,
    remove_pre_commit_config,
    uninstall_pre_commit_hooks,
)
from usethis._integrations.pre_commit.hooks import add_placeholder_hook, get_hook_names
from usethis._integrations.pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._integrations.ruff.rules import deselect_ruff_rules, select_ruff_rules
from usethis._integrations.uv.deps import add_deps_to_group, remove_deps_from_group
from usethis._tool import (
    ALL_TOOLS,
    DeptryTool,
    PreCommitTool,
    PyprojectFmtTool,
    PytestTool,
    RuffTool,
)


def use_deptry(*, remove: bool = False) -> None:
    tool = DeptryTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_configs()

        box_print("Call the 'deptry src' command to run deptry.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_configs()
        remove_deps_from_group(tool.dev_deps, "dev")


def use_pre_commit(*, remove: bool = False) -> None:
    tool = PreCommitTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        for _tool in ALL_TOOLS:
            if _tool.is_used():
                _tool.add_pre_commit_repo_configs()
        if not get_hook_names():
            add_placeholder_hook()

        install_pre_commit_hooks()

        if is_bitbucket_used():
            add_bitbucket_pre_commit_step()

        box_print(
            "Call the 'pre-commit run --all-files' command to run the hooks manually."
        )
    else:
        if is_bitbucket_used():
            remove_bitbucket_pre_commit_step()

        # Need pre-commit to be installed so we can uninstall hooks
        add_deps_to_group(tool.dev_deps, "dev")

        uninstall_pre_commit_hooks()
        remove_pre_commit_config()
        remove_deps_from_group(tool.dev_deps, "dev")

        # Need to add a new way of running some hooks manually if they are not dev
        # dependencies yet
        if PyprojectFmtTool().is_used():
            use_pyproject_fmt()


def use_pyproject_fmt(*, remove: bool = False) -> None:
    tool = PyprojectFmtTool()

    if not remove:
        is_pre_commit = PreCommitTool().is_used()

        if not is_pre_commit:
            add_deps_to_group(tool.dev_deps, "dev")
        else:
            tool.add_pre_commit_repo_configs()

        tool.add_pyproject_configs()

        if not is_pre_commit:
            box_print(
                "Call the 'pyproject-fmt pyproject.toml' command to run pyproject-fmt."
            )
        else:
            box_print(
                "Call the 'pre-commit run pyproject-fmt --all-files' command to run pyproject-fmt."
            )
    else:
        tool.remove_pyproject_configs()
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_configs()
        remove_deps_from_group(tool.dev_deps, "dev")


def use_pytest(*, remove: bool = False) -> None:
    tool = PytestTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "test")
        tool.add_pyproject_configs()
        if RuffTool().is_used():
            select_ruff_rules(tool.get_associated_ruff_rules())
        # deptry currently can't scan the tests folder for dev deps
        # https://github.com/fpgmaas/deptry/issues/302
        add_pytest_dir()

        if is_bitbucket_used():
            add_bitbucket_pytest_steps()

        box_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        box_print("Add test functions with the format 'test_*()'.")
        box_print("Call the 'pytest' command to run the tests.")
    else:
        if is_bitbucket_used():
            remove_bitbucket_pytest_steps()

        if RuffTool().is_used():
            deselect_ruff_rules(tool.get_associated_ruff_rules())
        tool.remove_pyproject_configs()
        remove_deps_from_group(tool.dev_deps, "test")
        remove_pytest_dir()  # Last, since this is a manual step


def use_ruff(*, remove: bool = False) -> None:
    tool = RuffTool()

    rules = [
        "A",
        "C4",
        "E4",
        "E7",
        "E9",
        "F",
        "FURB",
        "I",
        "PLE",
        "PLR",
        "RUF",
        "SIM",
        "UP",
    ]
    for _tool in ALL_TOOLS:
        if _tool.is_used():
            rules += _tool.get_associated_ruff_rules()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        tool.add_pyproject_configs()
        select_ruff_rules(rules)
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_configs()

        box_print(
            "Call the 'ruff check --fix' command to run the ruff linter with autofixes."
        )
        box_print("Call the 'ruff format' command to run the ruff formatter.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_configs()
        tool.remove_pyproject_configs()  # N.B. this will remove the selected ruff rules
        remove_deps_from_group(tool.dev_deps, "dev")
