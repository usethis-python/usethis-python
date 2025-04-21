from __future__ import annotations

from usethis._integrations.file.ini.errors import (
    INIError,
    ININotFoundError,
    INIValueAlreadySetError,
    INIValueMissingError,
    UnexpectedINIIOError,
    UnexpectedINIOpenError,
)


class SetupCFGError(INIError):
    """Raised when aspects of 'setup.cfg' are missing, invalid, or unexpected."""


class SetupCFGNotFoundError(SetupCFGError, ININotFoundError):
    """Raised when a setup.cfg file is not found."""


class SetupCFGDecodeError(SetupCFGError):
    """Raised when a setup.cfg file cannot be decoded."""


class UnexpectedSetupCFGOpenError(SetupCFGError, UnexpectedINIOpenError):
    """Raised when the setup.cfg file is unexpectedly opened."""


class UnexpectedSetupCFGIOError(SetupCFGError, UnexpectedINIIOError):
    """Raised when an unexpected attempt is made to read or write the setup.cfg file."""


class SetupCFGValueAlreadySetError(SetupCFGError, INIValueAlreadySetError):
    """Raised when a value is unexpectedly already set in the 'setup.cfg' file."""


class SetupCFGValueMissingError(SetupCFGError, INIValueMissingError):
    """Raised when a value is unexpectedly missing from the 'setup.cfg' file."""
