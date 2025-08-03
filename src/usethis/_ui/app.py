"""The Typer application for usethis."""

import typer

import usethis._ui.interface.author
import usethis._ui.interface.badge
import usethis._ui.interface.browse
import usethis._ui.interface.ci
import usethis._ui.interface.doc
import usethis._ui.interface.docstyle
import usethis._ui.interface.format_
import usethis._ui.interface.init
import usethis._ui.interface.lint
import usethis._ui.interface.list
import usethis._ui.interface.readme
import usethis._ui.interface.rule
import usethis._ui.interface.show
import usethis._ui.interface.spellcheck
import usethis._ui.interface.status
import usethis._ui.interface.test
import usethis._ui.interface.tool
import usethis._ui.interface.version

app = typer.Typer(
    help=(
        "Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    ),
    add_completion=False,
)

rich_help_panel = "Start a New Project"
app.command(
    name="init",
    help="Initialize a new project with recommended defaults.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.init.init,
)

rich_help_panel = "Manage Tooling"
app.command(
    help="Add or configure recommended documentation tools.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.doc.doc,
)
app.command(
    name="format",
    help="Add or configure recommended formatters.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.format_.format_,
)
app.command(
    help="Add or configure recommended linters.", rich_help_panel=rich_help_panel
)(
    usethis._ui.interface.lint.lint,
)
app.command(
    help="Add or configure a recommended spellchecker.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.spellcheck.spellcheck,
)
app.command(
    help="Add or configure a recommended testing framework.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.test.test,
)
app.add_typer(usethis._ui.interface.ci.app, name="ci", rich_help_panel=rich_help_panel)
app.add_typer(
    usethis._ui.interface.tool.app, name="tool", rich_help_panel=rich_help_panel
)

rich_help_panel = "Manage Configuration"
app.command(help="Add an author to the project.", rich_help_panel=rich_help_panel)(
    usethis._ui.interface.author.author,
)
app.command(help="Enforce a docstring style.", rich_help_panel=rich_help_panel)(
    usethis._ui.interface.docstyle.docstyle,
)
app.command(
    help="Enable a lint rule for the project.", rich_help_panel=rich_help_panel
)(
    usethis._ui.interface.rule.rule,
)
app.command(
    help="Set the development status of the project (via trove classifiers).",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.status.status,
)

rich_help_panel = "Manage the README"
app.add_typer(
    usethis._ui.interface.badge.app, name="badge", rich_help_panel=rich_help_panel
)
app.command(
    help="Add a README.md file to the project.", rich_help_panel=rich_help_panel
)(
    usethis._ui.interface.readme.readme,
)

rich_help_panel = "Informative"
app.add_typer(
    usethis._ui.interface.browse.app, name="browse", rich_help_panel=rich_help_panel
)
app.command(
    help="List usage of tooling and config managed by usethis.",
    rich_help_panel=rich_help_panel,
)(
    usethis._ui.interface.list.list,
)
app.add_typer(
    usethis._ui.interface.show.app, name="show", rich_help_panel=rich_help_panel
)
app.command(help="Display the version of usethis.", rich_help_panel=rich_help_panel)(
    usethis._ui.interface.version.version,
)
