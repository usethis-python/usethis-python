"""Utilities for Python version information."""

from __future__ import annotations

import re
from dataclasses import dataclass
from sysconfig import get_python_version as _get_python_version


class PythonVersionParseError(ValueError):
    """Raised when a Python version string cannot be parsed."""


@dataclass(frozen=True)
class PythonVersion:
    """Represents a Python version with major.minor.patch components.

    All components are stored as strings to handle alpha versions like 3.14.0a3.

    Examples:
        3.10.5 → major="3", minor="10", patch="5"
        3.13 → major="3", minor="13", patch=None
        3.14.0a3 → major="3", minor="14", patch="0a3"
    """

    major: str
    minor: str
    patch: str | None = None

    @classmethod
    def from_string(cls, version: str) -> PythonVersion:
        """Parse version string like '3.10.5' or '3.13' or '3.14.0a3'."""
        match = re.match(r"^(\d+)\.(\d+)(?:\.(\S+))?", version)
        if match is None:
            msg = f"Could not parse Python version from '{version}'."
            raise PythonVersionParseError(msg)

        major = match.group(1)
        minor = match.group(2)
        patch = match.group(3) if match.group(3) else None
        return cls(major=major, minor=minor, patch=patch)

    def to_short_string(self) -> str:
        """Return X.Y format (e.g., '3.10')."""
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        """Return full version string."""
        if self.patch is None:
            return self.to_short_string()
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_interpreter(cls) -> PythonVersion:
        """Get the Python version from the current interpreter."""
        return cls.from_string(_get_python_version())
