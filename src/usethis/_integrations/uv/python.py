import re

from usethis._config import usethis_config
from usethis._integrations.pyproject.requires_python import get_requires_python
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVUnparsedPythonVersionError


def get_available_python_versions() -> set[str]:
    if not usethis_config.offline:
        output = call_uv_subprocess(["python", "list", "--all-versions"])
    else:
        output = call_uv_subprocess(["python", "list", "--all-versions", "--offline"])

    return {
        _parse_python_version_from_uv_output(version) for version in output.splitlines()
    }


def get_supported_major_python_versions() -> list[int]:
    requires_python = get_requires_python()

    versions = set()
    for version in get_available_python_versions():
        # N.B. a standard range won't include alpha versions.
        if requires_python.contains(version):
            versions.add(version)

    return sorted({_get_major_version(version) for version in versions})


def _get_major_version(version: str) -> int:
    return int(version.split(".")[1])


def _parse_python_version_from_uv_output(version: str) -> str:
    match = re.match(r"^[A-z]*-(\d+.\d+.\d+[a-z\d]*)+[+-].*$", version)

    if match:
        return match.group(1)
    else:
        msg = f"Could not parse version from {version}"
        raise UVUnparsedPythonVersionError(msg)


def python_pin(version: str) -> None:
    call_uv_subprocess(["python", "pin", version])
