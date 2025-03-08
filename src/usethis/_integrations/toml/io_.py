from __future__ import annotations

from typing import TYPE_CHECKING

from tomlkit.exceptions import TOMLKitError

from usethis._integrations.toml.errors import (
    TOMLDecodeError,
    TOMLNotFoundError,
    UnexpectedTOMLIOError,
    UnexpectedTOMLOpenError,
)
from usethis._io import (
    UnexpectedFileIOError,
    UnexpectedFileOpenError,
    UsethisFileManager,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from tomlkit import TOMLDocument
    from typing_extensions import Self


class TOMLFileManager(UsethisFileManager):
    _content_by_path: ClassVar[dict[Path, TOMLDocument | None]] = {}

    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedFileOpenError as err:
            raise UnexpectedTOMLOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except FileNotFoundError as err:
            raise TOMLNotFoundError(err) from None
        except UnexpectedFileIOError as err:
            raise UnexpectedTOMLIOError(err) from None
        except TOMLKitError as err:
            msg = f"Failed to decode '{self.name}': {err}"
            raise TOMLDecodeError(msg) from None

    def get(self) -> TOMLDocument:
        return super().get()

    def commit(self, document: TOMLDocument) -> None:
        return super().commit(document)

    @property
    def _content(self) -> TOMLDocument | None:
        return super()._content

    @_content.setter
    def _content(self, value: TOMLDocument | None) -> None:
        self._content_by_path[self._path] = value  # TODO find a way to use super

    def _validate_lock(self) -> None:
        try:
            super()._validate_lock()
        except UnexpectedFileIOError as err:
            raise UnexpectedTOMLIOError(err) from None
