from __future__ import annotations

import subprocess


class SubprocessFailedError(Exception):
    pass


def call_subprocess(args: list[str]) -> str:
    try:
        process = subprocess.run(
            args,
            check=True,
            capture_output=True,
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
