import contextlib
import shutil
import sys

from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str]) -> str:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    try:
        return call_subprocess(["uv", *args])
    except SubprocessFailedError:
        # Perhaps there is a permissions error with the .venv folder? In which
        # case, we might be able to recover by deleting it.
        # Only applicable in Windows
        if sys.platform == "win32":
            with contextlib.suppress(PermissionError):
                shutil.rmtree(".venv")

        try:
            return call_subprocess(["uv", *args])
        except SubprocessFailedError as err:
            raise UVSubprocessFailedError(err) from None
