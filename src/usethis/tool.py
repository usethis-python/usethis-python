import contextlib

import typer

from usethis import console
from usethis._pre_commit.core import (
    add_pre_commit_config,
    install_pre_commit,
    remove_pre_commit_config,
    uninstall_pre_commit,
)
from usethis._pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._ruff.core import deselect_ruff_rules, select_ruff_rules
from usethis._tool import ALL_TOOLS, DeptryTool, PreCommitTool, PytestTool, RuffTool

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pre-commit instead of adding it."
    ),
) -> None:
    _pre_commit(remove=remove)


def _pre_commit(*, remove: bool = False) -> None:
    tool = PreCommitTool()

    if not remove:
        tool.add_dev_deps()
        add_pre_commit_config()
        for tool in ALL_TOOLS:
            if tool.is_used():
                tool.add_pre_commit_repo_config()
        install_pre_commit()

        console.print(
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.",
        )
    else:
        tool.add_dev_deps()  # Need pre-commit to be installed so we can uninstall hooks
        uninstall_pre_commit()
        remove_pre_commit_config()
        tool.remove_dev_deps()


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry(
    remove: bool = typer.Option(
        False, "--remove", help="Remove deptry instead of adding it."
    ),
) -> None:
    _deptry(remove=remove)


def _deptry(*, remove: bool = False) -> None:
    tool = DeptryTool()

    if not remove:
        tool.add_dev_deps()
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        console.print(
            "☐ Call the 'deptry src' command to run deptry.",
        )
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_dev_deps()


@app.command(help="Use ruff: an extremely fast Python linter and code formatter.")
def ruff(
    remove: bool = typer.Option(
        False, "--remove", help="Remove ruff instead of adding it."
    ),
) -> None:
    _ruff(remove=remove)


def _ruff(*, remove: bool = False) -> None:
    tool = RuffTool()

    rules = []
    for _tool in ALL_TOOLS:
        with contextlib.suppress(NotImplementedError):
            rules += _tool.get_associated_ruff_rules()

    if not remove:
        tool.add_dev_deps()
        tool.add_pyproject_configs()
        select_ruff_rules(rules)
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        console.print(
            "☐ Call the 'ruff check' command to run the ruff linter.\n"
            "☐ Call the 'ruff format' command to run the ruff formatter.",
        )
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_pyproject_configs()  # N.B. this will remove the selected ruff rules
        tool.remove_dev_deps()


@app.command(help="Use the pytest testing framework.")
def pytest(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pytest instead of adding it."
    ),
) -> None:
    _pytest(remove=remove)


def _pytest(*, remove: bool = False) -> None:
    tool = PytestTool()

    if not remove:
        tool.add_dev_deps()
        tool.add_pyproject_configs()
        if RuffTool().is_used():
            select_ruff_rules(tool.get_associated_ruff_rules())
        # deptry currently can't scan the tests folder for dev deps
        # https://github.com/fpgmaas/deptry/issues/302
        add_pytest_dir()

        console.print(
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Call the 'pytest' command to run the tests.",
        )
    else:
        if RuffTool().is_used():
            deselect_ruff_rules(tool.get_associated_ruff_rules())
        tool.remove_pyproject_configs()
        tool.remove_dev_deps()
        remove_pytest_dir()  # Last, since this is a manual step
