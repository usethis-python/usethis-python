from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.pyproject.errors import PyProjectTOMLInitError
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVSubprocessFailedError


def ensure_pyproject_toml() -> None:
    """Create a pyproject.toml file using `uv init`."""
    if (Path.cwd() / "pyproject.toml").exists():
        return

    is_hello_py = (Path.cwd() / "hello.py").exists()

    tick_print("Writing 'pyproject.toml'.")
    try:
        call_uv_subprocess(
            [
                "init",
                "--no-pin-python",
                "--no-readme",
                "--vcs=none",
                "--author-from=auto",
            ]
        )
    except UVSubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file:\n{err}"
        raise PyProjectTOMLInitError(msg) from None

    if not is_hello_py:
        # Delete the generated 'hello.py' file
        Path.unlink(Path.cwd() / "hello.py")
