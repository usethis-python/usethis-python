"""Subprocess invocation utilities."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class SubprocessFailedError(Exception):
    pass


@dataclass
class SubprocessResult:
    """The result of a successful subprocess invocation."""

    stdout: str
    stderr: str


def call_subprocess(args: list[str], *, cwd: Path | None = None) -> SubprocessResult:
    """Run a subprocess and return its output, raising SubprocessFailedError on failure."""
    try:
        process = subprocess.run(  # noqa: S603
            args, check=True, capture_output=True, cwd=cwd.as_posix() if cwd else None
        )
        return SubprocessResult(
            stdout=process.stdout.decode(),
            stderr=process.stderr.decode(),
        )
    except subprocess.CalledProcessError as err:
        bmsg_stderr: bytes = err.stderr
        bmsg_stdout: bytes = err.stdout

        stderr = bmsg_stderr.decode()
        stdout = bmsg_stdout.decode()

        msg = "Failed to run subprocess:"
        msg += f"\n  {' '.join(args)}"
        if stderr:
            msg += f"\n{stderr=}"
        if stdout:
            msg += f"\n{stdout=}"
        raise SubprocessFailedError(msg) from None
