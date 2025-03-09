from __future__ import annotations

import codecs
import sys

from rich.console import Console

from usethis._config import usethis_config

# Unicode support - but we need to be able to write bytes
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

console = Console()


def tick_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        console.print(
            f"{'✔'.encode('utf-8', 'ignore').decode('utf-8')} {msg}", style="green"
        )


def box_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        console.print(f"☐ {msg}", style="red")


def info_print(msg: str | Exception, temporary: bool = False) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        if temporary:
            end = "\r"
        else:
            end = "\n"
        console.print(f"ℹ {msg}", style="blue", end=end)  # noqa: RUF001


def err_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        console.print(f"✗ {msg}", style="red")


def warn_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        console.print(f"⚠ {msg}", style="yellow")
