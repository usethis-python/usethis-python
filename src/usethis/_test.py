from __future__ import annotations

import os
import socket
from contextlib import contextmanager
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any

from typer.testing import CliRunner as TyperCliRunner  # noqa: TID251

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
    with usethis_config.set(project_dir=new_dir):
        yield
    os.chdir(old_dir)


def is_offline() -> bool:
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
        input: bytes | str | IO[Any] | None = None,  # noqa: A002
        env: Mapping[str, str] | None = None,
        color: bool = False,
        **extra: Any,
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

    def invoke(  # noqa: PLR0913
        self,
        app: Typer,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[Any] | None = None,  # noqa: A002
        env: Mapping[str, str] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
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
