"""Central module for hard-coded fallback version constants.

These versions are manually bumped when necessary. Each constant corresponds to a
recent release of the respective tool. Associated up-to-dateness tests are in
`tests/usethis/test_fallback.py`.
"""

from packaging.version import Version

FALLBACK_UV_VERSION = "0.10.12"
FALLBACK_HATCHLING_VERSION = "1.29.0"
FALLBACK_PRE_COMMIT_VERSION = "4.5.1"
FALLBACK_RUFF_VERSION = "v0.15.7"
FALLBACK_SYNC_WITH_UV_VERSION = "v0.5.0"
FALLBACK_PYPROJECT_FMT_VERSION = "v2.20.0"
FALLBACK_CODESPELL_VERSION = "v2.4.2"


def next_breaking_version(version: str) -> str:
    """Get the next breaking version for a version string, following semver.

    For versions with major >= 1, bumps the major version (e.g. 1.0.2 -> 2.0.0).
    For versions with major == 0, bumps the minor version (e.g. 0.10.2 -> 0.11.0).
    """
    v = Version(version)
    if v.major >= 1:
        return f"{v.major + 1}.0.0"
    return f"0.{v.minor + 1}.0"
