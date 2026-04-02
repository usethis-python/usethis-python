"""Access the [project] section of pyproject.toml."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectSectionError,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._validate import validate_or_raise

if TYPE_CHECKING:
    from typing import Any


def get_project_dict() -> dict[str, Any]:
    """Get the contents of the [project] section from pyproject.toml."""
    pyproject = PyprojectTOMLManager().get().value

    try:
        raw_project = pyproject["project"]
    except KeyError:
        msg = "The 'project' section is missing from 'pyproject.toml'."
        raise PyprojectTOMLProjectSectionError(msg) from None

    return validate_or_raise(
        dict,
        raw_project,
        error_cls=PyprojectTOMLProjectSectionError,
        error_msg="The 'project' section in 'pyproject.toml' is not a valid map.",
    )
