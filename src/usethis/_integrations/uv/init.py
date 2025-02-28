from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.pyproject_toml.errors import PyprojectTOMLInitError
from usethis._integrations.uv import call
from usethis._integrations.uv.errors import UVSubprocessFailedError


def ensure_pyproject_toml() -> None:
    """Create a pyproject.toml file using `uv init --bare`."""
    if (Path.cwd() / "pyproject.toml").exists():
        return

    tick_print("Writing 'pyproject.toml'.")
    try:
        call.call_uv_subprocess(
            [
                "init",
                "--bare",
                "--vcs=none",
                "--author-from=auto",
            ],
            change_toml=True,
        )
    except UVSubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file:\n{err}"
        raise PyprojectTOMLInitError(msg) from None
