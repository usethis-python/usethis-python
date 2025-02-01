from typing import Any

from pydantic import TypeAdapter, ValidationError

from usethis._integrations.pyproject.errors import PyProjectTOMLProjectSectionError
from usethis._integrations.pyproject.io_ import read_pyproject_toml


def get_project_dict() -> dict[str, Any]:
    pyproject = read_pyproject_toml().value

    try:
        project = TypeAdapter(dict).validate_python(pyproject["project"])
    except KeyError:
        msg = "The 'project' section is missing from 'pyproject.toml'."
        raise PyProjectTOMLProjectSectionError(msg)
    except ValidationError as err:
        msg = f"The 'project' section in 'pyproject.toml' is not a valid map: {err}"
        raise PyProjectTOMLProjectSectionError(msg)

    return project
