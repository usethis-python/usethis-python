from packaging.specifiers import SpecifierSet

from usethis._integrations.pyproject.io import read_pyproject_toml

MIN_MAJOR_PY3 = 7  # Any earlier and uv won't support the executable.
MAX_MAJOR_PY3 = 13


class MissingRequiresPythonError(Exception):
    """Raised when the 'requires-python' key is missing."""


def get_requires_python() -> SpecifierSet:
    pyproject = read_pyproject_toml()

    try:
        requires_python = pyproject["project"]["requires-python"]
    except KeyError:
        raise MissingRequiresPythonError(
            "The [project.requires-python] value is missing from 'pyproject.toml'."
        )

    return SpecifierSet(requires_python)


def get_supported_major_python_versions() -> list[int]:
    requires_python = get_requires_python()

    versions = []
    for maj in range(MIN_MAJOR_PY3, MAX_MAJOR_PY3 + 1):
        if requires_python.contains(f"3.{maj}.0"):
            versions.append(maj)

    return versions
