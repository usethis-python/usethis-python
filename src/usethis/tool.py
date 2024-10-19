import typer

from usethis._pre_commit.core import ensure_pre_commit_config, install_pre_commit
from usethis._tool import ALL_TOOLS, DeptryTool, PreCommitTool, RuffTool

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit() -> None:
    tool = PreCommitTool()
    tool.ensure_dev_dep()
    ensure_pre_commit_config()
    for tool in ALL_TOOLS:
        if tool.is_used():
            tool.add_pre_commit_repo_config()
    install_pre_commit()


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry() -> None:
    tool = DeptryTool()
    tool.ensure_dev_dep()
    if PreCommitTool().is_used():
        tool.add_pre_commit_repo_config()


@app.command(help="Use ruff: an extremely fast Python linter and code formatter.")
def ruff() -> None:
    tool = RuffTool()
    tool.ensure_dev_dep()
    tool.add_pyproject_config()
    if PreCommitTool().is_used():
        tool.add_pre_commit_repo_config()
