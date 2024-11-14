from pydantic import TypeAdapter, ValidationError

from usethis._integrations.pyproject.errors import PyProjectTOMLProjectNameError
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
