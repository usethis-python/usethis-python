from rich.console import Console

from usethis._config import usethis_config

console = Console()


def tick_print(msg: str) -> None:
    if not usethis_config.quiet:
        console.print(f"✔ {msg}", style="green")


def box_print(msg: str) -> None:
    if not usethis_config.quiet:
        console.print(f"☐ {msg}", style="blue")
