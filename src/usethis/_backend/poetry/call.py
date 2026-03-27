"""Subprocess wrappers for invoking Poetry commands."""

from __future__ import annotations

from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.valid import ensure_pyproject_validity
from usethis._subprocess import SubprocessFailedError, call_subprocess
from usethis._types.backend import BackendEnum
from usethis.errors import ForbiddenBackendError


def call_poetry_subprocess(args: list[str], *, change_toml: bool) -> str:
    """Run a subprocess using the Poetry command-line tool.

    Returns:
        str: The output of the subprocess.

    Raises:
        PoetrySubprocessFailedError: If the subprocess fails.
        ForbiddenBackendError: If the current backend is not poetry (or auto).
    """
    if usethis_config.backend not in {BackendEnum.poetry, BackendEnum.auto}:
        msg = f"The '{usethis_config.backend.value}' backend is enabled, but a Poetry subprocess was invoked."
        raise ForbiddenBackendError(msg)

    if change_toml:
        _prepare_pyproject_write()

    new_args = ["poetry", *args]

    if usethis_config.subprocess_verbose:
        new_args = [*new_args[:1], "-vvv", *new_args[1:]]
    elif args[:1] != ["--version"]:
        new_args = [*new_args[:1], "--quiet", *new_args[1:]]

    new_args = [*new_args, "--no-interaction"]

    try:
        output = call_subprocess(
            new_args, cwd=usethis_config.cpd() if args[0] != "init" else None
        )
    except SubprocessFailedError as err:
        raise PoetrySubprocessFailedError(err) from None

    if change_toml and PyprojectTOMLManager().is_locked():
        PyprojectTOMLManager().read_file()

    return output


def _prepare_pyproject_write() -> None:
    is_pyproject_toml = (usethis_config.cpd() / "pyproject.toml").exists()
    is_locked = PyprojectTOMLManager().is_locked()

    if is_pyproject_toml and is_locked:
        ensure_pyproject_validity()
        PyprojectTOMLManager().write_file()
        PyprojectTOMLManager().revert()
    elif not is_pyproject_toml and is_locked:
        PyprojectTOMLManager().revert()
    elif is_pyproject_toml:
        with PyprojectTOMLManager():
            ensure_pyproject_validity()
