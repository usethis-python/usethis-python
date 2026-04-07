from pathlib import Path

import pytest

from _test import change_cwd
from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._deps import add_deps_to_group
from usethis._integrations.pre_commit.core import (
    install_pre_commit_hooks,
    remove_pre_commit_config,
    uninstall_pre_commit_hooks,
)
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._integrations.pre_commit.hooks import add_placeholder_hook
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency
from usethis.errors import BackendSubprocessFailedError


class TestRemovePreCommitConfig:
    def test_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(tmp_path):
            remove_pre_commit_config()

        # Assert
        assert not (tmp_path / ".pre-commit-config.yaml").exists()

    def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Removing '.pre-commit-config.yaml'.\n"

    def test_already_missing(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert not (tmp_path / ".pre-commit-config.yaml").exists()

    def test_does_not_exist(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            remove_pre_commit_config()

        # Assert
        assert not (tmp_path / ".pre-commit-config.yaml").exists()


class TestInstallPreCommitHooks:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_message(self, uv_env_dir: Path, capfd: pytest.CaptureFixture[str]):
        # This is needed to check the standard (non-frozen) message

        # Arrange
        with change_cwd(uv_env_dir), files_manager():
            add_deps_to_group([Dependency(name="pre-commit")], "dev")
            add_placeholder_hook()
            capfd.readouterr()

            # Act
            install_pre_commit_hooks()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Ensuring pre-commit is installed to Git.\n"
                "✔ Ensuring pre-commit hooks are installed.\n"
                "ℹ This may take a minute or so while the hooks are downloaded.\r"  # noqa: RUF001
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_frozen_message_using_uv(
        self, uv_init_repo_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        with change_cwd(uv_init_repo_dir), files_manager():
            add_deps_to_group([Dependency(name="pre-commit")], "dev")
            add_placeholder_hook()
            capfd.readouterr()

            # Act
            install_pre_commit_hooks()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'uv run pre-commit install' to register pre-commit.\n"
            )

    def test_frozen_message_using_poetry(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / "poetry.lock").touch()
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=True),
        ):
            # Act
            install_pre_commit_hooks()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'poetry run pre-commit install' to register pre-commit.\n"
            )

    def test_frozen_message_poetry_not_detected(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # When poetry backend is set but no poetry.lock exists
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=True),
        ):
            # Act
            install_pre_commit_hooks()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'pre-commit install' to register pre-commit.\n")

    def test_poetry_backend_install(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        # Arrange - mock call_backend_subprocess to avoid needing real poetry/pre-commit
        calls: list[list[str]] = []

        def mock_call_backend_subprocess(args: list[str], **__: object) -> None:
            calls.append(args)

        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core.call_backend_subprocess",
            mock_call_backend_subprocess,
        )
        # Mock git repo check so the hooks installation proceeds
        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core._is_git_repo",
            lambda: True,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=False),
        ):
            # Act
            install_pre_commit_hooks()

        # Assert - should have called install and install-hooks
        assert len(calls) == 2
        assert calls[0] == ["run", "pre-commit", "install"]
        assert calls[1] == ["run", "pre-commit", "install-hooks"]

    def test_poetry_backend_install_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        def mock_call_backend_subprocess(args: list[str], **__: object) -> None:
            _ = args
            raise BackendSubprocessFailedError

        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core.call_backend_subprocess",
            mock_call_backend_subprocess,
        )
        # Mock git repo check so the error path is exercised
        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core._is_git_repo",
            lambda: True,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=False),
            pytest.raises(PreCommitInstallationError),
        ):
            install_pre_commit_hooks()

    def test_no_git_repo(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # When not in a git repository, installation is skipped with an info message.
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.uv),
        ):
            install_pre_commit_hooks()

        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "ℹ Git is not available; skipping pre-commit hook installation.\n"  # noqa: RUF001
            "☐ Run 'pre-commit install' to register pre-commit.\n"
        )

    def test_none_backend(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").touch()

        # Act, Assert there is no error
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
            install_pre_commit_hooks()


class TestUninstallPreCommitHooks:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_message_and_file(
        self,
        uv_env_dir: Path,
        capfd: pytest.CaptureFixture[str],
    ):
        # This is needed to check the standard (non-frozen) message

        # Arrange
        with change_cwd(uv_env_dir), files_manager():
            add_deps_to_group([Dependency(name="pre-commit")], "dev")
            add_placeholder_hook()
            capfd.readouterr()

            # Act
            uninstall_pre_commit_hooks()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Ensuring pre-commit hooks are uninstalled.\n"

        # Uninstalling the hooks shouldn't remove the config file
        assert (uv_env_dir / ".pre-commit-config.yaml").exists()

    def test_no_git_repo(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # When not in a git repository, uninstallation is skipped with an info message.
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.uv),
        ):
            uninstall_pre_commit_hooks()

        out, err = capfd.readouterr()
        assert not err
        assert (
            out == "ℹ Git is not available; skipping pre-commit hook uninstallation.\n"  # noqa: RUF001
        )

    def test_none_backend(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").touch()

        # Act, Assert there is no error
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
            uninstall_pre_commit_hooks()

    def test_poetry_backend_uninstall(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        calls: list[list[str]] = []

        def mock_call_poetry_subprocess(args: list[str], **__: object) -> str:
            calls.append(args)
            return ""

        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core.call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )
        # Mock git repo check so the uninstall logic proceeds
        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core._is_git_repo",
            lambda: True,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=False),
        ):
            uninstall_pre_commit_hooks()

        # pre-commit uninstall succeeds on first try
        assert len(calls) == 1
        assert calls[0] == ["run", "pre-commit", "uninstall"]

    def test_poetry_backend_uninstall_pre_commit_not_installed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """When pre-commit is not installed, it should be temporarily added."""
        calls: list[list[str]] = []
        first_attempt = True

        def mock_call_poetry_subprocess(args: list[str], **__: object) -> str:
            nonlocal first_attempt
            calls.append(args)
            # First "run pre-commit uninstall" fails (pre-commit not installed)
            if args == ["run", "pre-commit", "uninstall"] and first_attempt:
                first_attempt = False
                _msg = "pre-commit not found"
                raise PoetrySubprocessFailedError(_msg)
            return ""

        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core.call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )
        # Mock git repo check so the uninstall logic proceeds
        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core._is_git_repo",
            lambda: True,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=False),
        ):
            uninstall_pre_commit_hooks()

        # First attempt fails, then: add pre-commit, run uninstall, remove pre-commit
        assert len(calls) == 4
        assert calls[0] == ["run", "pre-commit", "uninstall"]
        assert calls[1] == ["add", "--group", "dev", "pre-commit"]
        assert calls[2] == ["run", "pre-commit", "uninstall"]
        assert calls[3] == ["remove", "--group", "dev", "pre-commit"]

    def test_poetry_backend_uninstall_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        _msg = "test error"

        def mock_call_poetry_subprocess(args: list[str], **__: object) -> str:
            _ = args
            raise PoetrySubprocessFailedError(_msg)

        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core.call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )
        # Mock git repo check so the error path is exercised
        monkeypatch.setattr(
            "usethis._integrations.pre_commit.core._is_git_repo",
            lambda: True,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=False),
            pytest.raises(PreCommitInstallationError),
        ):
            uninstall_pre_commit_hooks()

    def test_frozen_poetry_instruction(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        (tmp_path / "poetry.lock").touch()
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry, frozen=True),
        ):
            uninstall_pre_commit_hooks()

        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "☐ Run 'poetry add --group dev pre-commit' to temporarily add pre-commit.\n"
            "☐ Run 'poetry run pre-commit uninstall' to deregister pre-commit.\n"
            "☐ Run 'poetry remove --group dev pre-commit' to remove pre-commit.\n"
        )

    def test_frozen_none_instruction(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.none, frozen=True),
        ):
            uninstall_pre_commit_hooks()

        out, err = capfd.readouterr()
        assert not err
        assert out == "☐ Run 'pre-commit uninstall' to deregister pre-commit.\n"
