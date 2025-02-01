from packaging.specifiers import SpecifierSet
from pydantic import TypeAdapter

from usethis._integrations.pyproject.io_ import read_pyproject_toml


class MissingRequiresPythonError(Exception):
    """Raised when the 'requires-python' key is missing."""


def get_requires_python() -> SpecifierSet:
    pyproject = read_pyproject_toml()

    try:
        requires_python = TypeAdapter(str).validate_python(
            TypeAdapter(dict).validate_python(pyproject["project"])["requires-python"]
        )
    except KeyError:
        msg = "The 'project.requires-python' value is missing from 'pyproject.toml'."
        raise MissingRequiresPythonError(msg)

    return SpecifierSet(requires_python)
