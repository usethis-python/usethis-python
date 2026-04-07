"""Test utilities and fixtures for the usethis test suite."""

from __future__ import annotations

import os
import socket
from contextlib import contextmanager
from pathlib import Path
from typing import IO, TYPE_CHECKING

from typer.testing import CliRunner as TyperCliRunner  # noqa: TID251
from typing_extensions import override

from usethis._config import usethis_config

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping, Sequence

    from click.testing import Result
    from typer import Typer


@contextmanager
def change_cwd(new_dir: Path) -> Generator[None, None, None]:
    """Change the working directory temporarily.

    Args:
        new_dir: The new directory to change to.
    """
    old_dir = Path.cwd()
    os.chdir(new_dir)
    try:
        with usethis_config.set(project_dir=new_dir):
            yield
    finally:
        os.chdir(old_dir)


def is_offline() -> bool:
    """Return True if the current environment has no internet connectivity."""
    try:
        # Connect to Google's DNS server
        s = socket.create_connection(("8.8.8.8", 53), timeout=3)
    except OSError:
        return True
    else:
        s.close()
        return False


class CliRunner(TyperCliRunner):
    def invoke_safe(
        self,
        app: Typer,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[str] | None = None,  # noqa: A002
        env: Mapping[str, str] | None = None,
        color: bool = False,
        **extra: object,
    ) -> Result:
        return self.invoke(
            app,
            args=args,
            input=input,
            env=env,
            catch_exceptions=False,
            color=color,
            **extra,
        )

    @override
    def invoke(
        self,
        app: Typer,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[str] | None = None,
        env: Mapping[str, str] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: object,
    ) -> Result:
        if catch_exceptions:
            msg = "`catch_exceptions=True` is forbidden in usethis tests. Use `.invoke_safe()` instead."
            raise NotImplementedError(msg)

        return super().invoke(
            app,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )
