from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str]) -> None:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    try:
        call_subprocess(["uv", *args])
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None
