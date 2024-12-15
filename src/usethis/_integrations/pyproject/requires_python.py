from packaging.specifiers import SpecifierSet
from pydantic import TypeAdapter

from usethis._integrations.pyproject.io import read_pyproject_toml

MIN_MAJOR_PY3 = 7  # Any earlier and uv won't support the executable.
MAX_MAJOR_PY3 = 13
_ALL_MAJOR_VERSIONS = list(range(MIN_MAJOR_PY3, MAX_MAJOR_PY3 + 1))


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


def get_supported_major_python_versions() -> list[int]:
    requires_python = get_requires_python()

    versions = []
    # TODO do something more graceful for older versions of Python rather than just
    # silently ignoring it.
    for maj in _ALL_MAJOR_VERSIONS:
        # TODO this won't work since .0 won't be in >=3.12.6 but we should definitely
        # test against 3.12.x in that case!
        if requires_python.contains(f"3.{maj}.0"):
            versions.append(maj)

    return versions
