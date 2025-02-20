from pathlib import Path

from usethis._config import usethis_config
from usethis._integrations.pyproject.io_ import (
    pyproject_toml_io_manager,
    read_pyproject_toml_from_path,
)
from usethis._integrations.pyproject.valid import ensure_pyproject_validity
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str], change_toml: bool) -> str:
    """Run a subprocess using the uv command-line tool.

    Returns:
        str: The output of the subprocess.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    is_pyproject_toml = (Path.cwd() / "pyproject.toml").exists()

    if is_pyproject_toml and change_toml:
        if pyproject_toml_io_manager._opener._set:
            ensure_pyproject_validity()
            pyproject_toml_io_manager._opener.write_file()
        else:
            with pyproject_toml_io_manager.open():
                ensure_pyproject_validity()

    read_pyproject_toml_from_path.cache_clear()

    if usethis_config.frozen and args[0] in {
        # Note, not "lock", for which the --frozen flags has quite a different effect
        "add",
        "remove",
        "sync",
        "export",
        "tree",
        "run",
    }:
        new_args = ["uv", args[0], "--frozen", *args[1:]]
    else:
        new_args = ["uv", *args]

    try:
        output = call_subprocess(new_args)
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None

    if change_toml and pyproject_toml_io_manager._opener._set:
        pyproject_toml_io_manager._opener.read_file()

    return output
