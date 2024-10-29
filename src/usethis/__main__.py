import typer

import usethis._interface.browse
import usethis._interface.ci
import usethis._interface.tool

app = typer.Typer(
    help=(
        "Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    )
)
app.add_typer(usethis._interface.tool.app, name="tool")
app.add_typer(usethis._interface.browse.app, name="browse")
app.add_typer(usethis._interface.ci.app, name="ci")
app(prog_name="usethis")

__all__ = ["app"]
