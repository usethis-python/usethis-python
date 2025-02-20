"""The Typer application for usethis."""

import typer

import usethis._interface.badge
import usethis._interface.browse
import usethis._interface.ci
import usethis._interface.readme
import usethis._interface.show
import usethis._interface.tool
import usethis._interface.version

app = typer.Typer(
    help=(
        "Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    )
)
app.add_typer(usethis._interface.badge.app, name="badge")
app.add_typer(usethis._interface.browse.app, name="browse")
app.add_typer(usethis._interface.ci.app, name="ci")
app.command(help="Add a README.md file to the project.")(
    usethis._interface.readme.readme,
)
app.add_typer(usethis._interface.show.app, name="show")
app.add_typer(usethis._interface.tool.app, name="tool")
app.command(help="Display the version of usethis.")(
    usethis._interface.version.version,
)
