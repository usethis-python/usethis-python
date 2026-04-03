"""Access the [project] section of pyproject.toml."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectSectionError,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager

if TYPE_CHECKING:
    from typing import Any


def get_project_dict() -> dict[str, Any]:
    """Get the contents of the [project] section from pyproject.toml."""
    return PyprojectTOMLManager().ensure_get(
        ["project"],
        err=PyprojectTOMLProjectSectionError(
            "The 'project' section is missing or invalid in 'pyproject.toml'."
        ),
        validate=dict,
    )
