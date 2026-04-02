"""Subprocess wrappers for invoking Poetry commands."""

from __future__ import annotations

from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.write import prepare_pyproject_write
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
        prepare_pyproject_write()

    # Poetry doesn't support a --frozen flag like uv does. The closest equivalent
    # is --lock, which updates pyproject.toml and the lockfile but skips installation.
    # Unlike uv's --frozen (which skips both locking and installation), Poetry's --lock
    # still resolves and updates poetry.lock. This is an acceptable compromise since
    # Poetry has no way to update pyproject.toml without also resolving dependencies.
    if usethis_config.frozen and args[:1] in (["add"], ["remove"]):
        args = [args[0], "--lock", *args[1:]]

    new_args = ["poetry", "--no-interaction", *args]

    if usethis_config.subprocess_verbose:
        new_args = [*new_args[:1], "-vvv", *new_args[1:]]
    elif args[:1] != ["--version"]:
        new_args = [*new_args[:1], "--quiet", *new_args[1:]]

    try:
        output = call_subprocess(new_args, cwd=usethis_config.cpd())
    except SubprocessFailedError as err:
        raise PoetrySubprocessFailedError(err) from None
    except FileNotFoundError:
        msg = "Poetry is not installed or not found on PATH."
        raise PoetrySubprocessFailedError(msg) from None

    if change_toml and PyprojectTOMLManager().is_locked():
        PyprojectTOMLManager().read_file()

    return output
