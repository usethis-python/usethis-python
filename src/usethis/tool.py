import subprocess

import typer

from usethis import console

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry() -> None:
    console.print("✔ Ensuring deptry is a development dependency", style="green")
    subprocess.run(["uv", "add", "--dev", "--quiet", "deptry"], check=True)


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commmit() -> None:
    console.print("✔ Ensuring pre-commit is a development dependency", style="green")
    subprocess.run(["uv", "add", "--dev", "--quiet", "pre-commit"], check=True)
