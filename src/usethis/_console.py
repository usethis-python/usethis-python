import typer
from rich.console import Console

console = Console()

offline_opt = typer.Option(False, "--offline", help="Disable network access")


def tick_print(msg: str, *, quiet: bool = False) -> None:
    if not quiet:
        console.print(f"✔ {msg}", style="green")


def box_print(msg: str, *, quiet: bool = False) -> None:
    if not quiet:
        console.print(f"☐ {msg}", style="blue")
