from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._integrations.file.ini.errors import (
    INIDecodeError,
    ININotFoundError,
    INIValueAlreadySetError,
    INIValueMissingError,
    UnexpectedINIIOError,
    UnexpectedINIOpenError,
)
from usethis._integrations.file.ini.io_ import INIFileManager
from usethis._integrations.file.setup_cfg.errors import (
    SetupCFGDecodeError,
    SetupCFGNotFoundError,
    SetupCFGValueAlreadySetError,
    SetupCFGValueMissingError,
    UnexpectedSetupCFGIOError,
    UnexpectedSetupCFGOpenError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from typing_extensions import Self

    from usethis._io import Key


class SetupCFGManager(INIFileManager):
    """Manages the setup.cfg file."""

    @property
    def relative_path(self) -> Path:
        return Path("setup.cfg")

    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedINIOpenError as err:
            raise UnexpectedSetupCFGOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except ININotFoundError as err:
            raise SetupCFGNotFoundError(err) from None
        except UnexpectedINIIOError as err:
            raise UnexpectedSetupCFGIOError(err) from None
        except INIDecodeError as err:
            raise SetupCFGDecodeError(err) from None

    def _validate_lock(self) -> None:
        try:
            super()._validate_lock()
        except UnexpectedINIIOError as err:
            raise UnexpectedSetupCFGIOError(err) from None

    def set_value(
        self, *, keys: Sequence[Key], value: Any, exists_ok: bool = False
    ) -> None:
        """Set a value in the pyproject.toml configuration file."""
        try:
            super().set_value(keys=keys, value=value, exists_ok=exists_ok)
        except INIValueAlreadySetError as err:
            raise SetupCFGValueAlreadySetError(err) from None

    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Remove a value from the pyproject.toml configuration file."""
        try:
            super().__delitem__(keys)
        except INIValueMissingError as err:
            raise SetupCFGValueMissingError(err) from None
