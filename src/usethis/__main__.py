import typer

import usethis.tool

app = typer.Typer(
    help=(
        "🤖 Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    )
)
app.add_typer(usethis.tool.app, name="tool")
app(prog_name="usethis")
