from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.pyproject.errors import PyProjectTOMLInitError
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVSubprocessFailedError


def ensure_pyproject_toml() -> None:
    """Create a pyproject.toml file using `uv init --bare`."""
    if (Path.cwd() / "pyproject.toml").exists():
        return

    tick_print("Writing 'pyproject.toml'.")
    try:
        call_uv_subprocess(
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
        raise PyProjectTOMLInitError(msg) from None
