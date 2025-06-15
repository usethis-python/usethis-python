from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class SubprocessFailedError(Exception):
    pass


def call_subprocess(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        process = subprocess.run(  # noqa: S603
            args, check=True, capture_output=True, cwd=cwd.as_posix() if cwd else None
        )
        return process.stdout.decode()
    except subprocess.CalledProcessError as err:
        bmsg_stderr: bytes = err.stderr
        bmsg_stdout: bytes = err.stdout

        stderr = bmsg_stderr.decode()
        stdout = bmsg_stdout.decode()

        msg = "Failed to run uv subprocess:"
        if stderr:
            msg += f"\n{stderr=}"
        if stdout:
            msg += f"\n{stdout=}"
        raise SubprocessFailedError(msg) from None
