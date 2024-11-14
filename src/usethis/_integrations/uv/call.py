import subprocess

from usethis._integrations.uv.errors import UVSubprocessFailedError


def call_subprocess(args: list[str]) -> None:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    try:
        subprocess.run(
            ["uv", *args],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as err:
        msg = f"Failed to run uv subprocess:\n{err.stderr.decode()}"
        raise UVSubprocessFailedError(msg) from None
