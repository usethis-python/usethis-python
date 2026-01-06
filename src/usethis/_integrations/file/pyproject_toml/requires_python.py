from __future__ import annotations

from packaging.specifiers import SpecifierSet
from pydantic import TypeAdapter

from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.python.version import PythonVersion


class MissingRequiresPythonError(Exception):
    """Raised when the 'requires-python' key is missing."""


def get_requires_python() -> SpecifierSet:
    pyproject = PyprojectTOMLManager().get()

    try:
        requires_python = TypeAdapter(str).validate_python(
            TypeAdapter(dict).validate_python(pyproject["project"])["requires-python"]
        )
    except KeyError:
        msg = "The 'project.requires-python' value is missing from 'pyproject.toml'."
        raise MissingRequiresPythonError(msg) from None

    return SpecifierSet(requires_python)


def get_required_minor_python_versions() -> list[PythonVersion]:
    """Get Python minor versions that match the project's requires-python constraint.

    Returns:
        List of Python versions within the requires-python bounds,
        sorted from lowest to highest. Empty list if no versions match.

    Raises:
        MissingRequiresPythonError: If requires-python is not specified.
        PyprojectTOMLNotFoundError: If pyproject.toml doesn't exist.
    """
    requires_python = get_requires_python()

    # Extract all versions mentioned in the specifier, grouped by (major, minor)
    versions_by_minor: dict[tuple[int, int], set[int]] = {}
    for spec in requires_python:
        parsed = PythonVersion.from_string(spec.version)
        major_minor = parsed.to_short_tuple()
        patch = int(parsed.patch) if parsed.patch else 0
        versions_by_minor.setdefault(major_minor, set()).add(patch)

    # Get overall bounds from what's explicitly in the specifier
    min_version = _get_minimum_minor_python_version_tuple(
        requires_python, versions_by_minor
    )
    max_version = _get_maximum_minor_python_version_tuple(
        requires_python, versions_by_minor
    )

    # If max_version is in a higher major version than min_version,
    # extend the previous major version to its hard-coded limit
    # E.g., >=3.6,<4.0 should include up to 3.15
    major_version_limits: dict[int, int] = {}
    if max_version[0] > min_version[0]:
        # We'll handle this by tracking which major versions need limits
        for major in range(min_version[0], max_version[0]):
            major_version_limits[major] = _get_maximum_python_minor_version(major)

    # Get minor version bounds from what's actually in the spec
    all_major_minors = list(versions_by_minor.keys())
    all_minors = [minor for _, minor in all_major_minors]
    min_minor_in_spec = min(all_minors)
    max_minor_in_spec = max(all_minors)

    supported_versions = []
    # Generate all major.minor combinations in range
    for major in range(min_version[0], max_version[0] + 1):
        min_minor = min_version[1] if major == min_version[0] else min_minor_in_spec
        # Apply hard-coded limit if this major version has one
        if major in major_version_limits:
            max_minor = major_version_limits[major]
        else:
            max_minor = max_version[1] if major == max_version[0] else max_minor_in_spec

        for minor in range(min_minor, max_minor + 1):
            version = PythonVersion(major=str(major), minor=str(minor), patch=None)
            version_str = version.to_short_string()

            # Get patch versions mentioned for this major.minor in the specifier
            # The extremes will lie +/- 1 from any named patch version
            patches_to_check = set()
            major_minor_key = (major, minor)
            if major_minor_key in versions_by_minor:
                for patch in versions_by_minor[major_minor_key]:
                    patches_to_check.add(max(0, patch - 1))
                    patches_to_check.add(patch)
                    patches_to_check.add(patch + 1)
            else:
                # No patch specified for this minor, default to checking .0
                patches_to_check.add(0)

            # Check if any of these patch versions satisfy the specifier
            is_valid = any(
                requires_python.contains(f"{version_str}.{patch}")
                for patch in patches_to_check
            )
            if is_valid:
                supported_versions.append(version)

    return supported_versions


def _get_minimum_minor_python_version_tuple(
    requires_python: SpecifierSet, versions_by_minor: dict[tuple[int, int], set[int]]
) -> tuple[int, int]:
    """Get the minimum (major, minor) Python version from requires-python specifier.

    Handles unbounded downward cases by applying hard-coded limits.

    Args:
        requires_python: The requires-python specifier set.
        versions_by_minor: Dict mapping (major, minor) to set of patch versions.

    Returns:
        Tuple of (major, minor) representing the minimum version.
    """
    all_major_minors = list(versions_by_minor.keys())
    min_version = min(all_major_minors)

    # Check if specifier is unbounded downward by testing min_version - 1 minor
    # Only test if min_minor > 0 (can't go below .0)
    is_unbounded_downward = min_version[1] > 0 and requires_python.contains(
        f"{min_version[0]}.{min_version[1] - 1}.0"
    )

    if is_unbounded_downward:
        if min_version[0] == 2:
            min_version = (2, 0)
        elif min_version[0] == 3:
            min_version = (3, 0)

    return min_version


def _get_maximum_minor_python_version_tuple(
    requires_python: SpecifierSet, versions_by_minor: dict[tuple[int, int], set[int]]
) -> tuple[int, int]:
    """Get the maximum (major, minor) Python version from requires-python specifier.

    Handles unbounded upward cases by applying hard-coded limits.

    Args:
        requires_python: The requires-python specifier set.
        versions_by_minor: Dict mapping (major, minor) to set of patch versions.

    Returns:
        Tuple of (major, minor) representing the maximum version.
    """
    all_major_minors = list(versions_by_minor.keys())
    max_version = max(all_major_minors)

    # Check if specifier is unbounded upward by testing max_version + 1 minor
    is_unbounded_upward = requires_python.contains(
        f"{max_version[0]}.{max_version[1] + 1}.0"
    )

    # Apply hard-coded limits for unbounded cases
    if is_unbounded_upward:
        max_version = (
            max_version[0],
            _get_maximum_python_minor_version(max_version[0]),
        )

    return max_version


def _get_maximum_python_minor_version(major: int) -> int:
    """Get the hard-coded maximum minor version for a given Python major version.

    Args:
        major: The Python major version (e.g., 2, 3). Usually will be 3.

    Returns:
        The maximum minor version for that major version.
    """
    if major == 2:
        return 7
    elif major == 3:
        # N.B. needs maintenance as new versions are released
        return 15
    else:
        raise NotImplementedError
