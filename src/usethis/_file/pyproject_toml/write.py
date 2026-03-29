"""Preparation helpers for writing pyproject.toml via subprocesses."""

from __future__ import annotations

from usethis._config import usethis_config
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.valid import ensure_pyproject_validity


def prepare_pyproject_write() -> None:
    """Prepare the pyproject.toml file for a subprocess that will modify it.

    When a managed PyprojectTOMLManager lock is held, this flushes pending
    in-memory changes to disk so the subprocess sees the latest state. After
    the subprocess runs, the caller should re-read the file to pick up any
    external modifications.
    """
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
