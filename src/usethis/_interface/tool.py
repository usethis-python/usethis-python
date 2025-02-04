import sys
from typing import Protocol

import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._console import err_print
from usethis._core.tool import (
    use_coverage,
    use_deptry,
    use_pre_commit,
    use_pyproject_fmt,
    use_pytest,
    use_requirements_txt,
    use_ruff,
)
from usethis.errors import UsethisError

app = typer.Typer(help="Add and configure development tools, e.g. linters.")

remove_opt = typer.Option(
    False, "--remove", help="Remove the tool instead of adding it."
)

frozen_opt = typer.Option(False, "--frozen", help="Use the frozen dependencies.")


@app.command(help="Use the coverage code coverage measurement tool.")
def coverage(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_coverage, remove=remove)


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_deptry, remove=remove)


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_pre_commit, remove=remove)


@app.command(
    help="Use the pyproject-fmt linter: opinionated formatting of 'pyproject.toml' files."
)
def pyproject_fmt(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_pyproject_fmt, remove=remove)


@app.command(help="Use the pytest testing framework.")
def pytest(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_pytest, remove=remove)


@app.command(
    name="requirements.txt",
    help="Use a requirements.txt file exported from the uv lockfile.",
)
def requirements_txt(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_requirements_txt, remove=remove)


@app.command(help="Use Ruff: an extremely fast Python linter and code formatter.")
def ruff(
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet, frozen=frozen):
        _run_tool(use_ruff, remove=remove)


class UseToolFunc(Protocol):
    def __call__(self, *, remove: bool) -> None: ...


def _run_tool(caller: UseToolFunc, *, remove: bool):
    try:
        caller(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)
