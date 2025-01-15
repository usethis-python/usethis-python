from pathlib import Path

from usethis._console import info_print, tick_print
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVSubprocessFailedError


def remove_pre_commit_config() -> None:
    name = ".pre-commit-config.yaml"
    if not (Path.cwd() / name).exists():
        # Early exit; the file already doesn't exist
        return

    tick_print(f"Removing '{name}'.")
    (Path.cwd() / name).unlink()


def install_pre_commit_hooks() -> None:
    """Install pre-commit hooks.

    Note that this requires pre-commit to be installed. It also requires the user to be
    in a git repo.
    """
    tick_print("Ensuring pre-commit is installed to Git.")
    try:
        call_uv_subprocess(["run", "pre-commit", "install"])
    except UVSubprocessFailedError as err:
        msg = f"Failed to install pre-commit in the Git repository:\n{err}"
        raise PreCommitInstallationError(msg) from None
    tick_print("Ensuring pre-commit hooks are installed.")
    info_print(
        "This may take a minute or so while the hooks are downloaded.", temporary=True
    )
    try:
        call_uv_subprocess(["run", "pre-commit", "install-hooks"])
    except UVSubprocessFailedError as err:
        msg = f"Failed to install pre-commit hooks:\n{err}"
        raise PreCommitInstallationError(msg) from None


def uninstall_pre_commit_hooks() -> None:
    """Uninstall pre-commit hooks.

    Note that this requires pre-commit to be installed. It also requires the user to be
    in a git repo.
    """
    tick_print("Ensuring pre-commit hooks are uninstalled.")
    try:
        call_uv_subprocess(["run", "pre-commit", "uninstall"])
    except UVSubprocessFailedError as err:
        msg = f"Failed to uninstall pre-commit hooks:\n{err}"
        raise PreCommitInstallationError(msg) from None
