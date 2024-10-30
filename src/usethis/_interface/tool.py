import contextlib

import typer

from usethis._console import console
from usethis._integrations.pre_commit.core import (
    add_pre_commit_config,
    install_pre_commit,
    remove_pre_commit_config,
    uninstall_pre_commit,
)
from usethis._integrations.pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._integrations.ruff.rules import deselect_ruff_rules, select_ruff_rules
from usethis._integrations.uv.deps import add_deps_to_group, remove_deps_from_group
from usethis._interface import offline_opt, quiet_opt
from usethis._tool import ALL_TOOLS, DeptryTool, PreCommitTool, PytestTool, RuffTool

app = typer.Typer(help="Add and configure development tools, e.g. linters.")


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pre-commit instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with console.set(quiet=quiet):
        _pre_commit(remove=remove, offline=offline)


def _pre_commit(*, remove: bool = False, offline: bool = False) -> None:
    tool = PreCommitTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev", offline=offline)
        add_pre_commit_config()
        for _tool in ALL_TOOLS:
            if _tool.is_used():
                _tool.add_pre_commit_repo_config()
        install_pre_commit()

        console.box_print(
            "Call the 'pre-commit run --all-files' command to run the hooks manually."
        )
    else:
        add_deps_to_group(  # Need pre-commit to be installed so we can uninstall hooks
            tool.dev_deps, "dev", offline=offline
        )
        uninstall_pre_commit()
        remove_pre_commit_config()
        remove_deps_from_group(tool.dev_deps, "dev", offline=offline)


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry(
    remove: bool = typer.Option(
        False, "--remove", help="Remove deptry instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with console.set(quiet=quiet):
        _deptry(remove=remove, offline=offline)


def _deptry(*, remove: bool = False, offline: bool = False) -> None:
    tool = DeptryTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev", offline=offline)
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        console.box_print("Call the 'deptry src' command to run deptry.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        remove_deps_from_group(tool.dev_deps, "dev", offline=offline)


@app.command(help="Use ruff: an extremely fast Python linter and code formatter.")
def ruff(
    remove: bool = typer.Option(
        False, "--remove", help="Remove ruff instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with console.set(quiet=quiet):
        _ruff(remove=remove, offline=offline)


def _ruff(*, remove: bool = False, offline: bool = False) -> None:
    tool = RuffTool()

    rules = []
    for _tool in ALL_TOOLS:
        if _tool.is_used() or _tool.name == "ruff":
            with contextlib.suppress(NotImplementedError):
                rules += _tool.get_associated_ruff_rules()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev", offline=offline)
        tool.add_pyproject_configs()
        select_ruff_rules(rules)
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        console.box_print(
            "Call the 'ruff check --fix' command to run the ruff linter with autofixes."
        )
        console.box_print("Call the 'ruff format' command to run the ruff formatter.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_pyproject_configs()  # N.B. this will remove the selected ruff rules
        remove_deps_from_group(tool.dev_deps, "dev", offline=offline)


@app.command(help="Use the pytest testing framework.")
def pytest(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pytest instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with console.set(quiet=quiet):
        _pytest(remove=remove, offline=offline)


def _pytest(*, remove: bool = False, offline: bool = False) -> None:
    tool = PytestTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "test", offline=offline)
        tool.add_pyproject_configs()
        if RuffTool().is_used():
            select_ruff_rules(tool.get_associated_ruff_rules())
        # deptry currently can't scan the tests folder for dev deps
        # https://github.com/fpgmaas/deptry/issues/302
        add_pytest_dir()

        console.box_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        console.box_print("Add test functions with the format 'test_*()'.")
        console.box_print("Call the 'pytest' command to run the tests.")
    else:
        if RuffTool().is_used():
            deselect_ruff_rules(tool.get_associated_ruff_rules())
        tool.remove_pyproject_configs()
        remove_deps_from_group(tool.dev_deps, "test", offline=offline)
        remove_pytest_dir()  # Last, since this is a manual step
