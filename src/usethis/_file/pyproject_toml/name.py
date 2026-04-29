"""Project name and description extraction from pyproject.toml."""

from __future__ import annotations

from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectDescriptionError,
    PyprojectTOMLProjectNameError,
)
from usethis._file.validate import validate_or_raise


def get_name() -> str:
    """Get the project name from pyproject.toml."""
    from usethis._file.pyproject_toml.project import get_project_dict  # noqa: PLC0415

    project_dict = get_project_dict()

    try:
        name = project_dict["name"]
    except KeyError:
        msg = "The 'project.name' value is missing from 'pyproject.toml'."
        raise PyprojectTOMLProjectNameError(msg) from None

    return validate_or_raise(
        str,
        name,
        err=PyprojectTOMLProjectNameError(
            "The 'project.name' value in 'pyproject.toml' is not a valid string."
        ),
    )


def get_description() -> str:
    """Get the project description from pyproject.toml."""
    from usethis._file.pyproject_toml.project import get_project_dict  # noqa: PLC0415

    project_dict = get_project_dict()

    try:
        description = project_dict["description"]
    except KeyError:
        msg = "The 'project.description' value is missing from 'pyproject.toml'."
        raise PyprojectTOMLProjectDescriptionError(msg) from None

    return validate_or_raise(
        str,
        description,
        err=PyprojectTOMLProjectDescriptionError(
            "The 'project.description' value in 'pyproject.toml' is not a valid string."
        ),
    )
