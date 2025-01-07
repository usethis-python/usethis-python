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
    for major_version in _ALL_MAJOR_VERSIONS:
        if is_major_python_version_supported(
            requires_python=requires_python, major_version=major_version
        ):
            versions.append(major_version)

    return versions


def is_major_python_version_supported(
    *, requires_python: SpecifierSet, major_version: int
) -> bool:
    return requires_python.contains(f"3.{major_version}.0")
