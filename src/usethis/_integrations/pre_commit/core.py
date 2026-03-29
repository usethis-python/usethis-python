"""Core pre-commit setup and teardown operations."""

from __future__ import annotations

import contextlib

from typing_extensions import assert_never

from usethis._backend.dispatch import call_backend_subprocess, get_backend
from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.detect import is_poetry_used
from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.detect import is_uv_used
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._console import info_print, instruct_print, tick_print
from usethis._deps import is_dep_in_any_group
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency
from usethis.errors import BackendSubprocessFailedError


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
        _instruct_pre_commit_install()
        return

    if backend in (BackendEnum.uv, BackendEnum.poetry):
        _run_pre_commit_install()
    elif backend is BackendEnum.none:
        instruct_print("Run 'pre-commit install' to install pre-commit to Git.")
    else:
        assert_never(backend)


def _instruct_pre_commit_install() -> None:
    backend = get_backend()
    if backend is BackendEnum.uv and is_uv_used():
        instruct_print("Run 'uv run pre-commit install' to register pre-commit.")
    elif backend is BackendEnum.poetry and is_poetry_used():
        instruct_print("Run 'poetry run pre-commit install' to register pre-commit.")
    elif backend in (BackendEnum.none, BackendEnum.uv, BackendEnum.poetry):
        instruct_print("Run 'pre-commit install' to register pre-commit.")
    else:
        assert_never(backend)


def _run_pre_commit_install() -> None:
    backend = get_backend()
    tick_print("Ensuring pre-commit is installed to Git.")
    try:
        call_backend_subprocess(
            ["run", "pre-commit", "install"],
            change_toml=False,
            backend=backend,
        )
    except BackendSubprocessFailedError as err:
        msg = f"Failed to install pre-commit in the Git repository:\n{err}"
        raise PreCommitInstallationError(msg) from None
    tick_print("Ensuring pre-commit hooks are installed.")
    info_print(
        "This may take a minute or so while the hooks are downloaded.",
        temporary=True,
    )
    try:
        call_backend_subprocess(
            ["run", "pre-commit", "install-hooks"],
            change_toml=False,
            backend=backend,
        )
    except BackendSubprocessFailedError as err:
        msg = f"Failed to install pre-commit hooks:\n{err}"
        raise PreCommitInstallationError(msg) from None


def uninstall_pre_commit_hooks() -> None:
    """Uninstall pre-commit hooks.

    Note that this requires the user to be in a git repo.
    """
    backend = get_backend()

    if usethis_config.frozen:
        _instruct_pre_commit_uninstall()
        return

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
    elif backend is BackendEnum.poetry:
        tick_print("Ensuring pre-commit hooks are uninstalled.")
        _run_poetry_pre_commit_uninstall()
    elif backend is BackendEnum.none:
        instruct_print("Run 'pre-commit uninstall' to deregister pre-commit.")
    else:
        assert_never(backend)


def _instruct_pre_commit_uninstall() -> None:
    backend = get_backend()
    if backend is BackendEnum.uv and is_uv_used():
        instruct_print(
            "Run 'uv run --with pre-commit pre-commit uninstall' to deregister pre-commit."
        )
    elif backend is BackendEnum.poetry and is_poetry_used():
        instruct_print(
            "Run 'poetry run pre-commit uninstall' to deregister pre-commit."
        )
    elif backend in (BackendEnum.none, BackendEnum.uv, BackendEnum.poetry):
        instruct_print("Run 'pre-commit uninstall' to deregister pre-commit.")
    else:
        assert_never(backend)


def _run_poetry_pre_commit_uninstall() -> None:
    pre_commit_dep = Dependency(name="pre-commit")
    already_installed = is_dep_in_any_group(pre_commit_dep)

    if not already_installed:
        # Temporarily add pre-commit so we can run it
        try:
            call_poetry_subprocess(
                ["add", "--group", "dev", "pre-commit"],
                change_toml=True,
            )
        except PoetrySubprocessFailedError as err:
            msg = f"Failed to temporarily add pre-commit:\n{err}"
            raise PreCommitInstallationError(msg) from None

    try:
        call_poetry_subprocess(
            ["run", "pre-commit", "uninstall"],
            change_toml=False,
        )
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to uninstall pre-commit hooks:\n{err}"
        raise PreCommitInstallationError(msg) from None
    finally:
        if not already_installed:
            # Remove the temporary pre-commit dependency
            with contextlib.suppress(PoetrySubprocessFailedError):
                call_poetry_subprocess(
                    ["remove", "--group", "dev", "pre-commit"],
                    change_toml=True,
                )
