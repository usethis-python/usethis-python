import json

from packaging.version import Version

from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError

FALLBACK_UV_VERSION = "0.10.12"


def get_uv_version() -> str:
    try:
        json_str = call_uv_subprocess(
            ["self", "version", "--output-format=json"],
            change_toml=False,
        )
    except UVSubprocessFailedError:
        return FALLBACK_UV_VERSION

    json_dict: dict = json.loads(json_str)
    return json_dict.get("version", FALLBACK_UV_VERSION)


def next_breaking_uv_version(version: str) -> str:
    """Get the next breaking version for a uv version string, following semver.

    For versions with major >= 1, bumps the major version (e.g. 1.0.2 -> 2.0.0).
    For versions with major == 0, bumps the minor version (e.g. 0.10.2 -> 0.11.0).
    """
    v = Version(version)
    if v.major >= 1:
        return f"{v.major + 1}.0.0"
    return f"0.{v.minor + 1}.0"
