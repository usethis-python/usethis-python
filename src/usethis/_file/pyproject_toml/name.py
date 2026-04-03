"""Project name and description extraction from pyproject.toml."""

from __future__ import annotations

from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectDescriptionError,
    PyprojectTOMLProjectNameError,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager


def get_name() -> str:
    """Get the project name from pyproject.toml."""
    return PyprojectTOMLManager().ensure_get(
        ["project", "name"],
        err=PyprojectTOMLProjectNameError(
            "The 'project.name' value is missing or invalid in 'pyproject.toml'."
        ),
        validate=str,
    )


def get_description() -> str:
    """Get the project description from pyproject.toml."""
    return PyprojectTOMLManager().ensure_get(
        ["project", "description"],
        err=PyprojectTOMLProjectDescriptionError(
            "The 'project.description' value is missing or invalid in 'pyproject.toml'."
        ),
        validate=str,
    )
