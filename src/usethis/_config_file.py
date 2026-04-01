"""Context managers for coordinated configuration file I/O."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import override

from usethis._backend.uv.toml import UVTOMLManager
from usethis._file.ini.io_ import INIFileManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._file.toml.io_ import TOMLFileManager
from usethis._file.yaml.io_ import YAMLFileManager
from usethis._integrations.pre_commit.yaml import PreCommitConfigYAMLManager

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextlib.contextmanager
def files_manager() -> Iterator[None]:
    """Context manager that opens all configuration file managers for coordinated I/O.

    On entry, this context manager locks every known configuration file manager. Each
    manager uses deferred (lazy) reads: a file is only read from disk the first time it
    is accessed via `get()`. In-memory changes made with `commit()` are immediately
    visible to other operations within the same context, even before they are written to
    disk.

    On exit, all modified files are written (flushed) to disk atomically. Files that were
    only read but never modified are not rewritten.

    Because writes are deferred until context exit, any operation that reads configuration
    files via the filesystem (e.g. a subprocess such as `ruff`, `pytest`, or
    `pre-commit`) will not see in-memory changes until the context manager has exited and
    the files have been flushed. If you need to run a subprocess that depends on
    configuration written by functions inside this context, exit the context first and
    then run the subprocess.
    """
    with (
        PyprojectTOMLManager(),
        SetupCFGManager(),
        DotCodespellRCManager(),
        DotCoverageRCManager(),
        DotCoverageRCTOMLManager(),
        DotRuffTOMLManager(),
        DotTyTOMLManager(),
        DotPytestINIManager(),
        DotImportLinterManager(),
        TachTOMLManager(),
        MkDocsYMLManager(),
        PreCommitConfigYAMLManager(),
        PytestINIManager(),
        RuffTOMLManager(),
        ToxINIManager(),
        TyTOMLManager(),
        UVTOMLManager(),
    ):
        yield


class DotCodespellRCManager(INIFileManager):
    """Class to manage the .codespellrc file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".codespellrc")


class DotCoverageRCManager(INIFileManager):
    """Class to manage the .coveragerc file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".coveragerc")


class DotCoverageRCTOMLManager(TOMLFileManager):
    """Class to manage the .coveragerc.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".coveragerc.toml")


class DotImportLinterManager(INIFileManager):
    """Class to manage the .importlinter file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".importlinter")


class DotPytestINIManager(INIFileManager):
    """Class to manage the .pytest.ini file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".pytest.ini")


class DotRuffTOMLManager(TOMLFileManager):
    """Class to manage the .ruff.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".ruff.toml")


class MkDocsYMLManager(YAMLFileManager):
    """Class to manage the mkdocs.yml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("mkdocs.yml")


class PytestINIManager(INIFileManager):
    """Class to manage the pytest.ini file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("pytest.ini")


class RuffTOMLManager(TOMLFileManager):
    """Class to manage the ruff.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("ruff.toml")


class TachTOMLManager(TOMLFileManager):
    """Class to manage the tach.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("tach.toml")


class ToxINIManager(INIFileManager):
    """Class to manage the tox.ini file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("tox.ini")


class DotTyTOMLManager(TOMLFileManager):
    """Class to manage the .ty.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".ty.toml")


class TyTOMLManager(TOMLFileManager):
    """Class to manage the ty.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("ty.toml")
