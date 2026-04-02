"""Project name and description extraction from pyproject.toml."""

from __future__ import annotations

from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectDescriptionError,
    PyprojectTOMLProjectNameError,
)
from usethis._file.pyproject_toml.project import get_project_dict
from usethis._validate import validate_or_raise


def get_name() -> str:
    """Get the project name from pyproject.toml."""
    project_dict = get_project_dict()

    try:
        raw_name = project_dict["name"]
    except KeyError:
        msg = "The 'project.name' value is missing from 'pyproject.toml'."
        raise PyprojectTOMLProjectNameError(msg) from None

    return validate_or_raise(
        str,
        raw_name,
        error_cls=PyprojectTOMLProjectNameError,
        error_msg="The 'project.name' value in 'pyproject.toml' is not a valid string.",
    )


def get_description() -> str:
    """Get the project description from pyproject.toml."""
    project_dict = get_project_dict()

    try:
        raw_description = project_dict["description"]
    except KeyError:
        msg = "The 'project.description' value is missing from 'pyproject.toml'."
        raise PyprojectTOMLProjectDescriptionError(msg) from None

    return validate_or_raise(
        str,
        raw_description,
        error_cls=PyprojectTOMLProjectDescriptionError,
        error_msg="The 'project.description' value in 'pyproject.toml' is not a valid string.",
    )
