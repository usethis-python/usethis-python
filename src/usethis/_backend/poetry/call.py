"""Subprocess wrappers for invoking Poetry commands."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._console import warn_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.write import prepare_pyproject_write
from usethis._subprocess import SubprocessFailedError, call_subprocess
from usethis._types.backend import BackendEnum
from usethis.errors import ForbiddenBackendError

if TYPE_CHECKING:
    from collections.abc import Generator


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

    # Poetry doesn't support a --frozen flag like uv does. To emulate frozen
    # behaviour we: (1) pass --lock to skip installation, (2) back up
    # poetry.lock before the subprocess and restore it afterwards so the
    # lockfile is never modified. This ensures pyproject.toml is updated by
    # the subprocess while the lockfile remains untouched.
    frozen_applicable = usethis_config.frozen and args[:1] in (["add"], ["remove"])
    if frozen_applicable:
        args = [args[0], "--lock", *args[1:]]

    new_args = ["poetry", "--no-interaction", *args]

    if usethis_config.subprocess_verbose:
        new_args = [*new_args[:1], "-vvv", *new_args[1:]]
    elif args[:1] != ["--version"]:
        new_args = [*new_args[:1], "--quiet", *new_args[1:]]

    lock_path = usethis_config.cpd() / "poetry.lock"
    with _frozen_poetry_lock(lock_path) if frozen_applicable else _noop_context():
        try:
            result = call_subprocess(new_args, cwd=usethis_config.cpd())
        except SubprocessFailedError as err:
            raise PoetrySubprocessFailedError(err) from None
        except FileNotFoundError:
            msg = "Poetry is not installed or not found on PATH."
            raise PoetrySubprocessFailedError(msg) from None

    _surface_stderr_warnings(result.stderr)

    if change_toml and PyprojectTOMLManager().is_locked():
        PyprojectTOMLManager().read_file()

    return result.stdout


@contextmanager
def _frozen_poetry_lock(lock_path: Path) -> Generator[None, None, None]:
    """Preserve the state of poetry.lock across the enclosed block.

    If the lockfile exists beforehand it is backed up and restored afterwards;
    if it did not exist, any lockfile created during the block is removed.
    """
    had_lockfile = lock_path.exists()
    tmp_dir = tempfile.mkdtemp()
    try:
        if had_lockfile:
            backup = Path(tmp_dir) / "poetry.lock"
            shutil.copy2(lock_path, backup)
        yield
    finally:
        if had_lockfile:
            shutil.copy2(Path(tmp_dir) / "poetry.lock", lock_path)
        elif lock_path.exists():
            lock_path.unlink()
        shutil.rmtree(tmp_dir)


@contextmanager
def _noop_context() -> Generator[None, None, None]:
    """A no-op context manager used when frozen mode is not applicable."""
    yield


def _surface_stderr_warnings(stderr: str) -> None:
    """Surface any warning lines from Poetry's stderr output."""
    for line in stderr.splitlines():
        stripped = line.strip()
        if stripped:
            warn_print(stripped)
