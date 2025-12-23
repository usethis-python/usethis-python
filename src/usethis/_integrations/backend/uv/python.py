from __future__ import annotations

import re

from usethis._integrations.backend.uv.call import call_uv_subprocess
from usethis._integrations.backend.uv.errors import UVUnparsedPythonVersionError
from usethis._integrations.file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._integrations.file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_requires_python,
)
from usethis._integrations.python.version import PythonVersion


def get_available_uv_python_versions() -> set[str]:
    output = call_uv_subprocess(["python", "list", "--all-versions"], change_toml=False)

    return {
        _parse_python_version_from_uv_output(version) for version in output.splitlines()
    }


def get_supported_uv_minor_python_versions() -> list[PythonVersion]:
    try:
        requires_python = get_requires_python()
    except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
        return [PythonVersion.from_interpreter()]

    versions = set()
    for version in get_available_uv_python_versions():
        # N.B. a standard range won't include alpha versions.
        if requires_python.contains(version):
            versions.add(version)

    # Extract unique minor versions and create PythonVersion objects with patch=None
    # Use (major, minor) tuple as key to avoid assuming major will always be 3
    version_objs = {PythonVersion.from_string(version) for version in versions}
    minor_versions: dict[tuple[str, str], PythonVersion] = {}
    for v in version_objs:
        key = (v.major, v.minor)
        if key not in minor_versions:
            # Create a new PythonVersion with just major.minor (patch=None)
            minor_versions[key] = PythonVersion(
                major=v.major, minor=v.minor, patch=None
            )

    return sorted(minor_versions.values(), key=lambda v: (int(v.major), int(v.minor)))


def _parse_python_version_from_uv_output(version: str) -> str:
    match = re.match(r"^[A-Za-z]*-(\d{1,2}.\d{1,2}.\d{1,2}[a-z\d]*)+[+-].*$", version)

    if match:
        return match.group(1)
    else:
        msg = f"Could not parse version from '{version}'."
        raise UVUnparsedPythonVersionError(msg)


def uv_python_pin(version: str) -> None:
    call_uv_subprocess(["python", "pin", version], change_toml=False)
