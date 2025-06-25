import typer

from usethis._config import (
    FROZEN_DEFAULT,
    HOW_DEFAULT,
    OFFLINE_DEFAULT,
    QUIET_DEFAULT,
    REMOVE_DEFAULT,
)

offline_opt = typer.Option(OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(QUIET_DEFAULT, "--quiet", help="Suppress output")
how_opt = typer.Option(
    HOW_DEFAULT,
    "--how",
    help="Only print how to use tools, do not add or remove them.",
)
remove_opt = typer.Option(
    REMOVE_DEFAULT, "--remove", help="Remove tools instead of adding them."
)
frozen_opt = typer.Option(
    FROZEN_DEFAULT,
    "--frozen",
    help="Do not install dependencies, nor update lockfiles.",
)
