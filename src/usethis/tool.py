import subprocess
from pathlib import Path

import typer

from usethis import console

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry() -> None:
    console.print("✔ Ensuring deptry is a development dependency", style="green")
    subprocess.run(["uv", "add", "--dev", "--quiet", "deptry"], check=True)


_CONTENTS = """
repos:
- repo: https://github.com/abravalheri/validate-pyproject
    rev: "v0.19"
    hooks:
    - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commmit() -> None:
    console.print("✔ Ensuring pre-commit is a development dependency", style="green")
    subprocess.run(["uv", "add", "--dev", "--quiet", "pre-commit"], check=True)

    # Check whether .pre-commit-config.yaml exists
    if not (Path.cwd() / ".pre-commit-config.yaml").exists():
        console.print("✔ Creating .pre-commit-config.yaml file", style="green")
        (Path.cwd() / ".pre-commit-config.yaml").write_text(_CONTENTS)
