import sys

import typer

from usethis._console import err_print
from usethis._integrations.pyproject.errors import PyProjectTOMLError
from usethis._integrations.pyproject.name import get_name

app = typer.Typer(help="Show information about the current project.")


@app.command(help="Show the name of the project")
def name() -> None:
    try:
        _name = get_name()
    except PyProjectTOMLError as err:
        err_print(err)
        sys.exit(1)

    print(_name)
