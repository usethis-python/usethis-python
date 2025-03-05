from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._integrations.pyproject_toml.errors import (
    PyprojectTOMLDecodeError,
    PyprojectTOMLNotFoundError,
    UnexpectedPyprojectTOMLIOError,
    UnexpectedPyprojectTOMLOpenError,
)
from usethis._integrations.toml.errors import (
    TOMLDecodeError,
    TOMLNotFoundError,
    UnexpectedTOMLIOError,
    UnexpectedTOMLOpenError,
)
from usethis._integrations.toml.io_ import TOMLFileManager

if TYPE_CHECKING:
    from typing_extensions import Self


class PyprojectTOMLManager(TOMLFileManager):
    """Manages the pyproject.toml file."""

    @property
    def relative_path(self) -> Path:
        return Path("pyproject.toml")

    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedTOMLOpenError as err:
            raise UnexpectedPyprojectTOMLOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except TOMLNotFoundError as err:
            raise PyprojectTOMLNotFoundError(err) from None
        except UnexpectedTOMLIOError as err:
            raise UnexpectedPyprojectTOMLIOError(err) from None
        except TOMLDecodeError as err:
            raise PyprojectTOMLDecodeError(err) from None

    def _validate_lock(self) -> None:
        try:
            super()._validate_lock()
        except UnexpectedTOMLIOError as err:
            raise UnexpectedPyprojectTOMLIOError(err) from None
