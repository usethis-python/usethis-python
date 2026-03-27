"""Check whether the Poetry CLI is available."""

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import PoetrySubprocessFailedError


def is_poetry_available() -> bool:
    """Check if the `poetry` command is available in the current environment."""
    try:
        call_poetry_subprocess(["--version"], change_toml=False)
    except PoetrySubprocessFailedError:
        return False

    return True
