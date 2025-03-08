from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from tomlkit.api import dumps, parse

from usethis.errors import UsethisError

if TYPE_CHECKING:
    from typing import Any, ClassVar, TypeAlias

    from typing_extensions import Self

    Document: TypeAlias = Any


class UnexpectedFileOpenError(UsethisError):
    """Raised when a file is unexpectedly opened."""


class UnexpectedFileIOError(UsethisError, IOError):
    """Raised when an unexpected attempt is made to read or write the pyproject.toml file."""


# TODO can we do variadic class for Document?
class UsethisFileManager:  # TODO mention deferred write logic. What is this approach called?
    _content_by_path: ClassVar[dict[Path, Document | None]] = {}

    @property
    @abstractmethod
    def relative_path(self) -> Path:
        """Return the relative path to the file."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.relative_path.name

    def __init__(self) -> None:
        self._path = (Path.cwd() / self.relative_path).resolve()

    def __enter__(self) -> Self:
        if self.is_locked():
            msg = (
                f"The '{self.name}' file is already in use by another instance of "
                f"'{self.__class__.__name__}'."
            )
            raise UnexpectedFileOpenError(msg)

        self.lock()
        return self

    def __exit__(self, exc_type: None, exc_value: None, traceback: None) -> None:
        if not self.is_locked():
            # This could happen if we decide to delete the file.
            return

        self.write_file()
        self.unlock()

    def get(self) -> Document:
        self._validate_lock()

        if self._content is None:
            self.read_file()
            assert self._content is not None

        return self._content

    def commit(self, document: Document) -> None:
        self._validate_lock()

        self._content = document

    def write_file(self) -> None:
        self._validate_lock()

        if self._content is None:
            # No changes made, nothing to write.
            return

        self._path.write_text(dumps(self._content))

    def read_file(self) -> None:
        self._validate_lock()

        if self._content is not None:
            msg = (
                f"The '{self.name}' file has already been read, use 'get()' to "
                f"access the content."
            )
            raise UnexpectedFileIOError(msg)
        try:
            self._content = parse(self._path.read_text())
        except FileNotFoundError:
            msg = f"'{self.name}' not found in the current directory at '{self._path}'"
            raise FileNotFoundError(msg) from None

    @property
    def _content(self) -> Document | None:
        return self._content_by_path[self._path]

    @_content.setter
    def _content(self, value: Document | None) -> None:
        self._content_by_path[self._path] = value

    def _validate_lock(self) -> None:
        if not self.is_locked():
            msg = (
                f"The '{self.name}' file has not been opened yet. Please enter the "
                f"context manager, e.g. 'with {self.__class__.__name__}():'"
            )
            raise UnexpectedFileIOError(msg)

    def is_locked(self) -> bool:
        return self._path in self._content_by_path

    def lock(self) -> None:
        self._content = None

    def unlock(self) -> None:
        self._content_by_path.pop(self._path, None)
