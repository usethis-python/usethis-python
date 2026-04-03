"""Subprocess wrappers for invoking Poetry commands."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

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
    backup_path = _backup_poetry_lock(lock_path) if frozen_applicable else None

    try:
        output = _run_poetry_subprocess(new_args)
    finally:
        if frozen_applicable:
            _restore_poetry_lock(lock_path, backup_path)

    if change_toml and PyprojectTOMLManager().is_locked():
        PyprojectTOMLManager().read_file()

    return output


def _run_poetry_subprocess(new_args: list[str]) -> str:
    """Execute the poetry subprocess, translating errors."""
    try:
        return call_subprocess(new_args, cwd=usethis_config.cpd())
    except SubprocessFailedError as err:
        raise PoetrySubprocessFailedError(err) from None
    except FileNotFoundError:
        msg = "Poetry is not installed or not found on PATH."
        raise PoetrySubprocessFailedError(msg) from None


def _backup_poetry_lock(lock_path: Path) -> Path | None:
    """Back up poetry.lock to a temp file. Returns the backup path, or None."""
    if not lock_path.exists():
        return None
    tmp_dir = tempfile.mkdtemp()
    backup = Path(tmp_dir) / "poetry.lock"
    shutil.copy2(lock_path, backup)
    return backup


def _restore_poetry_lock(lock_path: Path, backup_path: Path | None) -> None:
    """Restore poetry.lock from backup, or remove it if there was no backup."""
    if backup_path is not None:
        shutil.copy2(backup_path, lock_path)
        shutil.rmtree(backup_path.parent)
    elif lock_path.exists():
        lock_path.unlink()
