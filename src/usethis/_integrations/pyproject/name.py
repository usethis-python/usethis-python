from pydantic import TypeAdapter, ValidationError

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLProjectDescriptionError,
    PyProjectTOMLProjectNameError,
)
from usethis._integrations.pyproject.project import get_project_dict


def get_name() -> str:
    project_dict = get_project_dict()

    try:
        name = TypeAdapter(str).validate_python(project_dict["name"])
    except KeyError:
        msg = "The 'project.name' value is missing from 'pyproject.toml'."
        raise PyProjectTOMLProjectNameError(msg)
    except ValidationError as err:
        msg = (
            f"The 'project.name' value in 'pyproject.toml' is not a valid string: {err}"
        )
        raise PyProjectTOMLProjectNameError(msg)

    return name


def get_description() -> str:
    project_dict = get_project_dict()

    try:
        description = TypeAdapter(str).validate_python(project_dict["description"])
    except KeyError:
        msg = "The 'project.description' value is missing from 'pyproject.toml'."
        raise PyProjectTOMLProjectDescriptionError(msg)
    except ValidationError as err:
        msg = f"The 'project.description' value in 'pyproject.toml' is not a valid string: {err}"
        raise PyProjectTOMLProjectDescriptionError(msg)

    return description
