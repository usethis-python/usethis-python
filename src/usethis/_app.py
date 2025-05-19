"""The Typer application for usethis."""

import typer

import usethis._interface.author
import usethis._interface.badge
import usethis._interface.browse
import usethis._interface.ci
import usethis._interface.docstyle
import usethis._interface.list
import usethis._interface.readme
import usethis._interface.rule
import usethis._interface.show
import usethis._interface.tool
import usethis._interface.version

app = typer.Typer(
    help=(
        "Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    ),
    add_completion=False,
)

rich_help_panel = "Manage Tooling"
app.add_typer(usethis._interface.ci.app, name="ci", rich_help_panel=rich_help_panel)
app.add_typer(usethis._interface.tool.app, name="tool", rich_help_panel=rich_help_panel)

rich_help_panel = "Manage Configuration"
app.command(help="Add an author to the project.", rich_help_panel=rich_help_panel)(
    usethis._interface.author.author,
)
app.command(help="Enforce a docstring style.", rich_help_panel=rich_help_panel)(
    usethis._interface.docstyle.docstyle,
)
app.command(
    help="Enable a lint rule for the project.", rich_help_panel=rich_help_panel
)(
    usethis._interface.rule.rule,
)

rich_help_panel = "Manage README"
app.add_typer(
    usethis._interface.badge.app, name="badge", rich_help_panel=rich_help_panel
)
app.command(
    help="Add a README.md file to the project.", rich_help_panel=rich_help_panel
)(
    usethis._interface.readme.readme,
)

rich_help_panel = "Informative"
app.add_typer(
    usethis._interface.browse.app, name="browse", rich_help_panel=rich_help_panel
)
app.command(
    help="List usage of tooling and config managed by usethis.",
    rich_help_panel=rich_help_panel,
)(
    usethis._interface.list.list,
)
app.add_typer(usethis._interface.show.app, name="show", rich_help_panel=rich_help_panel)
app.command(help="Display the version of usethis.", rich_help_panel=rich_help_panel)(
    usethis._interface.version.version,
)
