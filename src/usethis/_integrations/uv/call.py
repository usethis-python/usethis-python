from usethis._integrations.pyproject.io import read_pyproject_toml_from_path
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str]) -> str:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    read_pyproject_toml_from_path.cache_clear()
    try:
        return call_subprocess(["uv", *args])
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None
