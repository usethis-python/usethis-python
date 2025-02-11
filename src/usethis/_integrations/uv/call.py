from usethis._config import usethis_config
from usethis._integrations.pyproject.io_ import read_pyproject_toml_from_path
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str]) -> str:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    read_pyproject_toml_from_path.cache_clear()

    if usethis_config.frozen and args[0] in {
        # Note, not "lock", for which the --frozen flags has quite a different effect
        "add",
        "remove",
        "sync",
        "export",
        "tree",
        "run",
    }:
        new_args = ["uv", args[0], "--frozen", *args[1:]]
    else:
        new_args = ["uv", *args]

    try:
        return call_subprocess(new_args)
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None
