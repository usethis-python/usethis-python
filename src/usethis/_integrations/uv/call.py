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
    new_args = ["uv", *args]
    if usethis_config.frozen:
        new_args.append("--frozen")
    try:
        return call_subprocess(new_args)
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None
