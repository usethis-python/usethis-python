import json

from usethis._integrations.backend.uv.call import call_uv_subprocess
from usethis._integrations.backend.uv.errors import UVSubprocessFailedError

FALLBACK_UV_VERSION = "0.9.20"


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
