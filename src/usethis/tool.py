import subprocess

import typer

app = typer.Typer(help="Add and configure development tools, e.g. linters")


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry() -> None:
    print("✔ Adding deptry as a development dependency")
    subprocess.run(["uv", "add", "--dev", "--quiet", "deptry"], check=True)
