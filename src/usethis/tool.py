import typer

from usethis._pre_commit.core import (
    ensure_pre_commit_config,
    install_pre_commit,
    remove_pre_commit_config,
    uninstall_pre_commit,
)
from usethis._tool import ALL_TOOLS, DeptryTool, PreCommitTool, RuffTool

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
        tool.ensure_dev_dep()
        ensure_pre_commit_config()
        for tool in ALL_TOOLS:
            if tool.is_used():
                tool.add_pre_commit_repo_config()
        install_pre_commit()
    else:
        uninstall_pre_commit()
        remove_pre_commit_config()
        tool.remove_dev_dep()


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
        tool.ensure_dev_dep()
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_dev_dep()


@app.command(help="Use ruff: an extremely fast Python linter and code formatter.")
def ruff(
    remove: bool = typer.Option(
        False, "--remove", help="Remove ruff instead of adding it."
    ),
) -> None:
    _ruff(remove=remove)


def _ruff(*, remove: bool = False) -> None:
    tool = RuffTool()

    if not remove:
        tool.ensure_dev_dep()
        tool.add_pyproject_config()
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_pyproject_config()
        tool.remove_dev_dep()
