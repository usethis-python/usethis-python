import typer

from usethis._config import (
    BACKEND_DEFAULT,
    BUILD_BACKEND_DEFAULT,
    FROZEN_DEFAULT,
    HOW_DEFAULT,
    OFFLINE_DEFAULT,
    QUIET_DEFAULT,
    REMOVE_DEFAULT,
)

# shared options
offline_opt = typer.Option(OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(QUIET_DEFAULT, "--quiet", help="Suppress output")
how_opt = typer.Option(
    HOW_DEFAULT,
    "--how",
    help="Only print how to use tools, do not add or remove them.",
)
remove_opt = typer.Option(
    REMOVE_DEFAULT, "--remove", help="Remove tools instead of adding them."
)
frozen_opt = typer.Option(
    FROZEN_DEFAULT,
    "--frozen",
    help="Do not install dependencies, nor update lockfiles.",
)
backend_opt = typer.Option(
    BACKEND_DEFAULT, "--backend", help="Package manager backend to use."
)
no_hook_opt = typer.Option(
    False, "--no-hook", help="Don't add or remove git hook configuration."
)

# author command options
author_name_opt = typer.Option(..., "--name", help="Author name")
author_email_opt = typer.Option("", "--email", help="Author email")
author_overwrite_opt = typer.Option(
    False, "--overwrite", help="Overwrite any existing authors"
)

# browse command options
browser_opt = typer.Option(
    False, "--browser", help="Open the URL in the default web browser."
)

# docstyle command options
docstyle_style_arg = typer.Argument(
    default="google", help="Docstring style to enforce."
)

# init command options
init_arch_opt = typer.Option(
    False, "--arch/--no-arch", help="Add recommended architecture analysis tools."
)
init_doc_opt = typer.Option(
    True, "--doc/--no-doc", help="Add a recommended documentation framework."
)
init_format_opt = typer.Option(
    True, "--format/--no-format", help="Add recommended formatters."
)
init_lint_opt = typer.Option(True, "--lint/--no-lint", help="Add recommended linters.")
init_spellcheck_opt = typer.Option(
    True,
    "--spellcheck/--no-spellcheck",
    help="Add a recommended spellchecker.",
)
init_test_opt = typer.Option(
    True,
    "--test/--no-test",
    help="Add a recommended testing framework.",
)
init_typecheck_opt = typer.Option(
    False,
    "--typecheck/--no-typecheck",
    help="Add a recommended type checker.",
)
init_hook_opt = typer.Option(
    False,
    "--hook/--no-hook",
    help="Add a recommended git hook framework.",
)
init_docstyle_opt = typer.Option(
    None,
    "--docstyle",
    help="Set a docstring style convention for the project.",
)
init_status_opt = typer.Option(
    "planning",
    "--status",
    help="Set the development status of the project.",
)
init_path_arg = typer.Argument(
    None,
    help="The path to use for the project. Defaults to the current working directory.",
)
init_build_backend_opt = typer.Option(
    BUILD_BACKEND_DEFAULT,
    "--build-backend",
    help="The build backend to use for the project.",
)

# readme command options
badges_opt = typer.Option(False, "--badges", help="Add relevant badges")

# status command options
status_arg = typer.Argument(default=..., help="Docstring style to enforce.")

# ruff command options
linter_opt = typer.Option(
    True,
    "--linter/--no-linter",
    help="Add or remove specifically the Ruff linter.",
)
formatter_opt = typer.Option(
    True,
    "--formatter/--no-formatter",
    help="Add or remove specifically the Ruff formatter.",
)
