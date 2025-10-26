from __future__ import annotations

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._console import info_print, instruct_print, tick_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.call import call_uv_subprocess
from usethis._integrations.backend.uv.errors import UVSubprocessFailedError
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._types.backend import BackendEnum


def remove_pre_commit_config() -> None:
    name = ".pre-commit-config.yaml"
    if not (usethis_config.cpd() / name).exists():
        # Early exit; the file already doesn't exist
        return

    tick_print(f"Removing '{name}'.")
    (usethis_config.cpd() / name).unlink()


def install_pre_commit_hooks() -> None:
    """Install pre-commit hooks.

    Note that this requires pre-commit to be installed. It also requires the user to be
    in a git repo.
    """
    backend = get_backend()

    if usethis_config.frozen:
        if backend is BackendEnum.uv and is_uv_used():
            instruct_print("Run 'uv run pre-commit install' to register pre-commit.")
        else:
            assert backend in (BackendEnum.none, BackendEnum.uv)
            instruct_print("Run 'pre-commit install' to register pre-commit.")
        return

    if backend is BackendEnum.uv:
        tick_print("Ensuring pre-commit is installed to Git.")
        try:
            call_uv_subprocess(["run", "pre-commit", "install"], change_toml=False)
        except UVSubprocessFailedError as err:
            msg = f"Failed to install pre-commit in the Git repository:\n{err}"
            raise PreCommitInstallationError(msg) from None
        tick_print("Ensuring pre-commit hooks are installed.")
        info_print(
            "This may take a minute or so while the hooks are downloaded.",
            temporary=True,
        )
        try:
            call_uv_subprocess(
                ["run", "pre-commit", "install-hooks"], change_toml=False
            )
        except UVSubprocessFailedError as err:
            msg = f"Failed to install pre-commit hooks:\n{err}"
            raise PreCommitInstallationError(msg) from None
    elif backend is BackendEnum.none:
        instruct_print("Run 'pre-commit install' to install pre-commit to Git.")
    else:
        assert_never(backend)


def uninstall_pre_commit_hooks() -> None:
    """Uninstall pre-commit hooks.

    Note that this requires the user to be in a git repo.
    """
    if usethis_config.frozen:
        instruct_print(
            "Run 'uv run --with pre-commit pre-commit uninstall' to deregister pre-commit."
        )
        return

    backend = get_backend()
    if backend is BackendEnum.uv:
        tick_print("Ensuring pre-commit hooks are uninstalled.")
        try:
            call_uv_subprocess(
                ["run", "--with", "pre-commit", "pre-commit", "uninstall"],
                change_toml=False,
            )
        except UVSubprocessFailedError as err:
            msg = f"Failed to uninstall pre-commit hooks:\n{err}"
            raise PreCommitInstallationError(msg) from None
    elif backend is BackendEnum.none:
        instruct_print("Run 'pre-commit uninstall' to deregister pre-commit.")
    else:
        assert_never(backend)
