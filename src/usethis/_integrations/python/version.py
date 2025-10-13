"""Utilities for Python version information."""

from __future__ import annotations

from sysconfig import get_python_version as _get_python_version


def get_python_version() -> str:
    """Get the Python version."""
    return _get_python_version()


def get_python_major_version() -> int:
    """Get the major version of Python."""
    return extract_major_version(get_python_version())


def extract_major_version(version: str) -> int:
    """Extract the major version from a version string."""
    return int(version.split(".")[1])
