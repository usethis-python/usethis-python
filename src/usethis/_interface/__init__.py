import typer

offline_opt = typer.Option(False, "--offline", help="Disable network access")
quiet_opt = typer.Option(False, "--quiet", help="Suppress output")
