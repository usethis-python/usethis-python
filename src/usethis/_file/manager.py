"""Base file manager classes for configuration file I/O."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, cast

from typing_extensions import override

from usethis._config import usethis_config
from usethis.errors import UsethisError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path
    from types import TracebackType
    from typing import ClassVar

    from typing_extensions import Self

    from usethis._file.types_ import Key


class Document(Protocol):
    """Protocol for the document type managed by FileManager."""

    pass


DocumentT = TypeVar("DocumentT", covariant=True)


class UnexpectedFileOpenError(UsethisError):
    """Raised when a file is unexpectedly opened."""


class UnexpectedFileIOError(UsethisError, IOError):
    """Raised when an unexpected attempt is made to read or write the pyproject.toml file."""


class FileManager(Generic[DocumentT], metaclass=ABCMeta):
    """Manages file access with deferred writes using a context manager.

    This class implements the Command Pattern, encapsulating file operations. It defers
    writing changes to the file until the context is exited, ensuring that file I/O
    operations are performed efficiently and only when necessary.

    Lifecycle:
        1. **Enter** (`__enter__`): The file is locked. No disk I/O occurs yet.
        2. **Read** (`get`): The file is lazily read from disk on first access. Subsequent
           calls return the in-memory copy.
        3. **Write** (`commit`): Changes are stored in memory and the file is marked dirty.
           The changes are immediately visible to other code that calls `get()` on the
           same manager within the same context, but they are *not* yet on disk.
        4. **Exit** (`__exit__`): All dirty files are flushed (written) to disk atomically.

    Because writes are deferred, subprocesses that read the managed file from the
    filesystem will not see uncommitted in-memory changes. Exit the context manager (or
    call `write_file()` explicitly) before invoking a subprocess that depends on the
    file's on-disk content.
    """

    # https://github.com/python/mypy/issues/5144
    # The Any in this expression should be identified with DocumentT
    _content_by_path: ClassVar[dict[Path, Any | None]] = {}
    _dirty_by_path: ClassVar[dict[Path, bool]] = {}
    path: Path

    @property
    @abstractmethod
    def relative_path(self) -> Path:
        """Return the relative path to the file."""
        raise NotImplementedError

    def __init__(self) -> None:
        self.path = (usethis_config.cpd() / self.relative_path).resolve()

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileManager):
            return NotImplemented

        return self.relative_path == other.relative_path

    @override
    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.relative_path))

    @property
    def name(self) -> str:
        return self.relative_path.name

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.relative_path.as_posix()!r})"

    def __enter__(self) -> Self:
        if self.is_locked():
            msg = (
                f"The '{self.name}' file is already in use by another instance of "
                f"'{self.__class__.__name__}'."
            )
            raise UnexpectedFileOpenError(msg)

        self.lock()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.is_locked():
            # This could happen if we decide to delete the file.
            return

        self.write_file()
        self.unlock()

    def get(self) -> DocumentT:
        """Retrieve the document, reading from disk if necessary."""
        self._validate_lock()

        if self._content is None:
            return self.read_file()
        else:
            return self._content

    def commit(self, document: DocumentT) -> None:  # pyright: ignore[reportGeneralTypeIssues] not modifying DocumentT so safe to use covariant type variable here
        """Store the given document in memory for deferred writing."""
        self._validate_lock()
        self._content = document
        self._dirty_by_path[self.path] = True

    def revert(self) -> None:
        """Clear the stored document without writing to disk."""
        self._content = None
        self._dirty_by_path[self.path] = False

    def write_file(self) -> None:
        """Write the stored document to disk if there are changes."""
        self._validate_lock()

        if self._content is None:
            # No changes made, nothing to write.
            return

        if not self._dirty_by_path.get(self.path, False):
            # Content was read but not modified via commit().
            return

        # Also, if the file has since been deleted, we should not write it.
        if not self.path.exists():
            return

        self.path.write_text(self._dump_content(), encoding="utf-8")

    def read_file(self) -> DocumentT:
        """Read the document from disk and store it in memory.

        Also returns the document.
        """
        self._validate_lock()

        if self._content is not None:
            msg = (
                f"The '{self.name}' file has already been read, use 'get()' to "
                f"access the content."
            )
            raise UnexpectedFileIOError(msg)
        try:
            document = self._parse_content(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            msg = f"'{self.name}' not found in the current directory at '{self.path}'."
            raise FileNotFoundError(msg) from None

        self._content = document

        return document

    @abstractmethod
    def _dump_content(self) -> str:
        """Return the content of the document as a string."""
        raise NotImplementedError

    @abstractmethod
    def _parse_content(self, content: str) -> DocumentT:
        """Parse the content of the document."""
        raise NotImplementedError

    @property
    def _content(self) -> DocumentT | None:
        return cast("DocumentT | None", self._content_by_path.get(self.path))

    @_content.setter
    def _content(self, value: DocumentT | None) -> None:
        self._content_by_path[self.path] = value

    def _validate_lock(self) -> None:
        if not self.is_locked():
            msg = (
                f"The '{self.name}' file has not been opened yet. Please enter the "
                f"context manager, e.g. 'with {self.__class__.__name__}():'."
            )
            raise UnexpectedFileIOError(msg)

    def is_locked(self) -> bool:
        return self.path in self._content_by_path

    def lock(self) -> None:
        self._content = None
        self._dirty_by_path[self.path] = False

    def unlock(self) -> None:
        self._content_by_path.pop(self.path, None)
        self._dirty_by_path.pop(self.path, None)


class KeyValueFileManager(
    FileManager[DocumentT], Generic[DocumentT], metaclass=ABCMeta
):
    """A manager for files which store (at least some) values in key-value mappings."""

    @abstractmethod
    def __contains__(self, keys: Sequence[Key]) -> bool:
        """Check if a key exists in the configuration file."""
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, keys: Sequence[Key]) -> object:
        raise NotImplementedError

    def __setitem__(self, keys: Sequence[Key], value: object) -> None:
        """Set a value in the configuration file."""
        return self.set_value(keys=keys, value=value, exists_ok=True)

    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Remove a value from the configuration file."""
        raise NotImplementedError

    def get_validated(
        self, keys: Sequence[Key], *, default: Any, validate: Any = None
    ) -> Any:
        """Retrieve a value by keys, returning ``default`` on missing key or failed validation.

        Args:
            keys: The key path to look up.
            default: The value to return when the key is missing or
                validation fails.  Required, no default.
            validate: An optional type to validate the retrieved value
                against (forwarded to ``TypeAdapter``).  When ``None``,
                no validation is performed.

        Returns:
            The (optionally validated) value, or ``default``.
        """
        try:
            raw = self[keys]
        except (KeyError, FileNotFoundError):
            return default

        if validate is None:
            return raw

        from usethis._file.validate import validate_or_default  # noqa: PLC0415

        return validate_or_default(validate, raw, default=default)

    def ensure_get(self, keys: Sequence[Key], *, err: Exception, validate: Any) -> Any:
        """Retrieve and validate a value by keys, raising ``err`` on failure.

        Args:
            keys: The key path to look up.
            err: An instantiated exception to raise when the key is
                missing or validation fails.
            validate: The type to validate the retrieved value against
                (forwarded to ``TypeAdapter``).  Required.

        Returns:
            The validated value.

        Raises:
            type(err): When the key is missing or the value does not
                conform to ``validate``.
        """
        try:
            raw = self[keys]
        except (KeyError, FileNotFoundError):
            raise err from None

        from usethis._file.validate import validate_or_raise  # noqa: PLC0415

        return validate_or_raise(
            validate,
            raw,
            error_cls=type(err),
            error_msg=str(err),
        )

    @abstractmethod
    def set_value(
        self, *, keys: Sequence[Key], value: object, exists_ok: bool = False
    ) -> None:
        """Set a value in the configuration file."""
        raise NotImplementedError

    @abstractmethod
    def extend_list(self, *, keys: Sequence[Key], values: Sequence[object]) -> None:
        """Extend a list in the configuration file.

        This method will always extend the list, even if it results in duplicates.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_from_list(
        self, *, keys: Sequence[Key], values: Sequence[object]
    ) -> None:
        """Remove values from a list in the configuration file."""
        raise NotImplementedError
