import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._core.badge import (
    Badge,
    add_badge,
    get_pre_commit_badge,
    get_pypi_badge,
    get_ruff_badge,
    get_usethis_badge,
    get_uv_badge,
    remove_badge,
)
from usethis.errors import UsethisError

app = typer.Typer(
    help="Add badges to the top of the README.md file.", add_completion=False
)

remove_opt = typer.Option(
    False, "--remove", help="Remove the badge instead of adding it."
)


@app.command(help="Add a badge with the version of your package on PyPI.")
def pypi(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _modify_badge(get_pypi_badge(), remove=remove)


@app.command(help="Add a badge for the Ruff linter.")
def ruff(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _modify_badge(get_ruff_badge(), remove=remove)


@app.command(help="Add a badge for the pre-commit framework.")
def pre_commit(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _modify_badge(get_pre_commit_badge(), remove=remove)


@app.command(help="Add a badge for usethis.")
def usethis(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _modify_badge(get_usethis_badge(), remove=remove)


@app.command(help="Add a badge for the uv package manager.")
def uv(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _modify_badge(get_uv_badge(), remove=remove)


def _modify_badge(
    badge: Badge,
    remove: bool = False,
):
    try:
        if not remove:
            add_badge(badge)
        else:
            remove_badge(badge)
    except UsethisError as err:
        err_print(err)
        raise typer.Exit(code=1) from None
