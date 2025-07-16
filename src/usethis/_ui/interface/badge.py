from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from usethis._ui.options import offline_opt, quiet_opt

if TYPE_CHECKING:
    from usethis._core.badge import Badge

app = typer.Typer(
    help="Add badges to the top of the README.md file.", add_completion=False
)

remove_opt = typer.Option(
    False, "--remove", help="Remove the badge instead of adding it."
)

show_opt = typer.Option(False, "--show", help="Print the badge to the console.")


@app.command(help="Add a badge with the version of your package on PyPI.")
def pypi(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    show: bool = show_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._core.badge import get_pypi_badge

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _badge_effect(get_pypi_badge(), remove=remove, show=show)


@app.command(help="Add a badge for the Ruff linter.")
def ruff(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    show: bool = show_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._core.badge import get_ruff_badge

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _badge_effect(get_ruff_badge(), remove=remove, show=show)


@app.command(help="Add a badge for the pre-commit framework.")
def pre_commit(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    show: bool = show_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._core.badge import get_pre_commit_badge

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _badge_effect(get_pre_commit_badge(), remove=remove, show=show)


@app.command(help="Add a badge for usethis.")
def usethis(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    show: bool = show_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._core.badge import get_usethis_badge

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _badge_effect(get_usethis_badge(), remove=remove, show=show)


@app.command(help="Add a badge for the uv package manager.")
def uv(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    show: bool = show_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._core.badge import get_uv_badge

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        _badge_effect(get_uv_badge(), remove=remove, show=show)


def _badge_effect(
    badge: Badge,
    remove: bool = False,
    show: bool = False,
):
    from usethis._console import err_print
    from usethis._core.badge import add_badge, remove_badge
    from usethis.errors import UsethisError

    try:
        if show:
            print(badge.markdown)
        elif not remove:
            add_badge(badge)
        else:
            remove_badge(badge)
    except UsethisError as err:
        err_print(err)
        raise typer.Exit(code=1) from None
