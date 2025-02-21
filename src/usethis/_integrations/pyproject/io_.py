from functools import cache
from pathlib import Path

from tomlkit.api import dumps, parse
from tomlkit.exceptions import TOMLKitError
from tomlkit.toml_document import TOMLDocument
from typing_extensions import Self

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLDecodeError,
    PyProjectTOMLNotFoundError,
)


def read_pyproject_toml() -> TOMLDocument:
    return pyproject_toml_io_manager._opener.read()


def write_pyproject_toml(toml_document: TOMLDocument) -> None:
    return pyproject_toml_io_manager._opener.write(toml_document)


@cache
def read_pyproject_toml_from_path(path: Path) -> TOMLDocument:
    try:
        return parse(path.read_text())
    except FileNotFoundError:
        msg = "'pyproject.toml' not found in the current directory."
        raise PyProjectTOMLNotFoundError(msg)
    except TOMLKitError as err:
        msg = f"Failed to decode 'pyproject.toml': {err}"
        raise PyProjectTOMLDecodeError(msg) from None


class UnexpectedPyprojectTOMLReadError(Exception):
    """Raised when the pyproject.toml is read unexpectedly."""


class PyprojectTOMLOpener:
    def __init__(self) -> None:
        self.path = Path.cwd() / "pyproject.toml"
        self.content = TOMLDocument()
        self.open = False
        self._set = False

    def read(self) -> TOMLDocument:
        if not self._set:
            msg = """The pyproject.toml opener has not been set yet."""
            raise UnexpectedPyprojectTOMLOpenError(msg)

        if not self.open:
            self.read_file()
            self.open = True

        return self.content

    def write(self, toml_document: TOMLDocument) -> None:
        if not self._set:
            msg = """The pyproject.toml opener has not been set yet."""
            raise UnexpectedPyprojectTOMLOpenError(msg)

        self.content = toml_document

    def write_file(self) -> None:
        read_pyproject_toml_from_path.cache_clear()
        self.path.write_text(dumps(self.content))

    def read_file(self) -> None:
        self.content = read_pyproject_toml_from_path(self.path)

    def __enter__(self) -> Self:
        self._set = True
        return self

    def __exit__(self, exc_type: None, exc_value: None, traceback: None) -> None:
        self.write_file()
        self._set = False


class UnexpectedPyprojectTOMLOpenError(Exception):
    """Raised when the pyproject.toml opener is accessed unexpectedly."""


class PyprojectTOMLIOManager:
    def __init__(self) -> None:
        self._opener = PyprojectTOMLOpener()
        self._set = False

    @property
    def opener(self) -> PyprojectTOMLOpener:
        if not self._opener._set:
            self._set = False

        if not self._set:
            msg = """The pyproject.toml opener has not been set to open yet."""
            raise UnexpectedPyprojectTOMLOpenError(msg)

        return self._opener

    def open(self) -> PyprojectTOMLOpener:
        self._opener = PyprojectTOMLOpener()
        return self._opener


pyproject_toml_io_manager = PyprojectTOMLIOManager()
