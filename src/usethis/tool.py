import typer

from usethis._pre_commit.core import install_pre_commit
from usethis._tool import ALL_TOOLS, DeptryTool, PreCommitTool

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry() -> None:
    tool = DeptryTool()
    tool.ensure_dev_dep()
    if PreCommitTool().is_used():
        tool.add_pre_commit_repo_config()


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit() -> None:
    tool = PreCommitTool()
    tool.ensure_dev_dep()
    for tool in ALL_TOOLS:
        if tool.is_used():
            tool.add_pre_commit_repo_config()
    install_pre_commit()
