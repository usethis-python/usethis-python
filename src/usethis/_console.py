import typer
from rich.console import Console

console = Console()

offline_opt = typer.Option(False, "--offline", help="Disable network access")
