from __future__ import annotations

import codecs
import functools
import sys
from typing import TYPE_CHECKING, Literal

from rich.console import Console

from usethis._config import usethis_config

if TYPE_CHECKING:
    from rich.table import Table

# Unicode support - but we need to be able to write bytes
try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
except AttributeError:
    # e.g. in Jupyter
    pass

console = Console()
err_console = Console(stderr=True)


def plain_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not (
        usethis_config.quiet
        or usethis_config.alert_only
        or usethis_config.instruct_only
    ):
        console.print(msg)


def table_print(table: Table) -> None:
    if not (
        usethis_config.quiet
        or usethis_config.alert_only
        or usethis_config.instruct_only
    ):
        console.print(table, justify="left", overflow="fold", soft_wrap=True)


def tick_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not (
        usethis_config.quiet
        or usethis_config.alert_only
        or usethis_config.instruct_only
    ):
        icon = _get_icon("tick")
        console.print(f"{icon} {msg}", style="green")


def instruct_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not (usethis_config.quiet or usethis_config.alert_only):
        icon = _get_icon("instruct")
        console.print(f"{icon} {msg}", style="red")


def how_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not (
        usethis_config.quiet
        or usethis_config.alert_only
        or usethis_config.instruct_only
    ):
        icon = _get_icon("how")
        console.print(f"{icon} {msg}", style="red")


def info_print(msg: str | Exception, temporary: bool = False) -> None:
    msg = str(msg)

    if not (
        usethis_config.quiet
        or usethis_config.alert_only
        or usethis_config.instruct_only
    ):
        icon = _get_icon("info")
        if temporary:
            end = "\r"
        else:
            end = "\n"
        console.print(f"{icon} {msg}", style="blue", end=end)


def err_print(msg: str | Exception) -> None:
    msg = str(msg)

    if not usethis_config.quiet:
        icon = _get_icon("error")
        err_console.print(f"{icon} {msg}", style="red")


def warn_print(msg: str | Exception) -> None:
    msg = str(msg)

    _cached_warn_print(msg)


@functools.cache
def _cached_warn_print(msg: str) -> None:
    if not usethis_config.quiet:
        icon = _get_icon("warning")
        console.print(f"{icon} {msg}", style="yellow")


# Icon fallback system for terminals with varying Unicode support
IconType = Literal["tick", "instruct", "how", "info", "error", "warning"]

_ICON_FALLBACKS: dict[IconType, tuple[str, str, str]] = {
    # Format: (unicode, universal, text)  # noqa: ERA001
    "tick": ("✔", "√", "[ok]"),
    "instruct": ("☐", "□", "[todo]"),
    "how": ("☐", "□", "[todo]"),
    "info": ("ℹ", "i", "[info]"),  # noqa: RUF001
    "error": ("✗", "×", "[error]"),  # noqa: RUF001
    "warning": ("⚠", "!", "[warning]"),
}


@functools.cache
def get_icon_mode() -> Literal["unicode", "universal", "text"]:
    """Detect terminal's icon support level.

    Tries to encode icons and returns the first level that works.
    Cached for performance.
    """
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"

    # Try unicode icons
    try:
        "✔☐ℹ✗⚠".encode(encoding)  # noqa: RUF001
        return "unicode"
    except (UnicodeEncodeError, LookupError):
        pass

    # Try universal icons
    try:
        "√□i×!".encode(encoding)  # noqa: RUF001
        return "universal"
    except (UnicodeEncodeError, LookupError):
        pass

    # Final fallback to text
    return "text"


def _get_icon(icon_type: IconType) -> str:
    """Get the appropriate icon based on terminal capabilities.

    Uses cached terminal detection for performance.
    """
    fallbacks = _ICON_FALLBACKS[icon_type]
    mode = get_icon_mode()

    if mode == "unicode":
        return fallbacks[0]
    elif mode == "universal":
        return fallbacks[1]
    else:
        return fallbacks[2]
