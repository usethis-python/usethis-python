from collections.abc import Generator
from contextlib import contextmanager

from pydantic import BaseModel
from rich.console import Console

typer_console = Console()


class UsethisConsole(BaseModel):
    quiet: bool

    def tick_print(self, msg: str) -> None:
        if not self.quiet:
            typer_console.print(f"✔ {msg}", style="green")

    def box_print(self, msg: str) -> None:
        if not self.quiet:
            typer_console.print(f"☐ {msg}", style="blue")

    @contextmanager
    def set(self, *, quiet: bool) -> Generator[None, None, None]:
        """Temporarily set the console to quiet mode."""
        self.quiet = quiet
        yield
        self.quiet = False


console = UsethisConsole(quiet=False)
