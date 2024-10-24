import typer

import usethis.browse
import usethis.ci
import usethis.tool

app = typer.Typer(
    help=(
        "🤖 Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    )
)
app.add_typer(usethis.tool.app, name="tool")
app.add_typer(usethis.browse.app, name="browse")
app.add_typer(usethis.ci.app, name="ci")
app(prog_name="usethis")
