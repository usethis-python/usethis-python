import contextlib
import shutil
import sys
from pathlib import Path

from usethis._console import warn_print
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str]) -> str:
    """Run a subprocess using the uv command-line tool.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    args = ["uv", *args]

    try:
        return call_subprocess(args)
    except SubprocessFailedError as err:
        # Perhaps there is a permissions error with the .venv folder? In which
        # case, we might be able to recover by deleting it.
        # Only applicable in Windows
        if sys.platform == "win32":
            with contextlib.suppress(PermissionError):
                warn_print(f"Failed to run uv subprocess: {' '.join(args)}")
                warn_print(
                    "Deleting the .venv folder and running 'uv sync` to try and recover..."
                )
                _del_dotvenv()

            try:
                call_subprocess(["uv", "sync"])
                return call_subprocess(args)
            except SubprocessFailedError as second_err:
                msg = (
                    f"Initially: {err}\n"
                    f"Then, after deleting the .venv folder: {second_err}"
                )
                raise UVSubprocessFailedError(msg)
        else:
            raise UVSubprocessFailedError(err) from None


def _del_dotvenv() -> None:
    # Iterate over the directory; only avoid deleting .venv/Scripts/usethis.exe
    with contextlib.suppress(SubprocessFailedError):
        call_subprocess(["uv", "pip", "uninstall", "usethis"])

    if not (Path.cwd() / ".venv").exists():
        return

    for _f in (Path.cwd() / ".venv").iterdir():
        if _f.name != "Scripts":
            _del_path(_f)
        else:
            if not _f.is_dir():
                msg = f"Expected a directory: {_f}"
                raise AssertionError(msg)

            for _f2 in _f.iterdir():
                if _f2.name != "usethis.exe":
                    _del_path(_f2)


def _del_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.is_file():
        path.unlink()
    else:
        msg = f"Unexpected file type: {path}"
        raise AssertionError(msg)
