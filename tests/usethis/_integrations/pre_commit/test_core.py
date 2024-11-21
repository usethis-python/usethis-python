from pathlib import Path

import pytest

# import requests
from usethis._integrations.pre_commit.core import (
    # _VALIDATEPYPROJECT_VERSION,
    # add_pre_commit_config_file,
    install_pre_commit_hooks,
    remove_pre_commit_config,
    uninstall_pre_commit_hooks,
)
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._integrations.pre_commit.hooks import add_placeholder_hook
from usethis._integrations.uv.deps import add_deps_to_group
from usethis._test import change_cwd

# class TestAddPreCommitConfigFile:
#     def test_exists(self, uv_init_dir: Path):
#         # Act
#         with change_cwd(uv_init_dir):
#             add_pre_commit_config_file()

#         # Assert
#         contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
#         assert contents == (
#             f"""\
# repos:
#   - repo: https://github.com/abravalheri/validate-pyproject
#     rev: "{_VALIDATEPYPROJECT_VERSION}"
#     hooks:
#       - id: validate-pyproject
#         additional_dependencies: ["validate-pyproject-schema-store[all]"]
# """
#         )

#     def test_fallback(self, uv_init_dir: Path, monkeypatch: pytest.MonkeyPatch):
#         # Arrange
#         def mock_get(*args, **kwargs):
#             class MockResponse:
#                 def raise_for_status(self):
#                     msg = "Failed to fetch tags"
#                     raise requests.exceptions.HTTPError(msg)

#             return MockResponse()

#         monkeypatch.setattr("requests.get", mock_get)

#         # Act
#         with change_cwd(uv_init_dir):
#             add_pre_commit_config_file()

#         # Assert
#         contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
#         assert contents == (
#             f"""\
# repos:
#   - repo: https://github.com/abravalheri/validate-pyproject
#     rev: "{_VALIDATEPYPROJECT_VERSION}"
#     hooks:
#       - id: validate-pyproject
#         additional_dependencies: ["validate-pyproject-schema-store[all]"]
# """
#         )

#     def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
#         # Act
#         with change_cwd(uv_init_dir):
#             add_pre_commit_config_file()

#         # Assert
#         out, _ = capfd.readouterr()
#         assert out == "✔ Writing '.pre-commit-config.yaml'.\n"

#     def test_already_exists(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
#         # Arrange
#         (uv_init_dir / ".pre-commit-config.yaml").touch()

#         # Act
#         with change_cwd(uv_init_dir):
#             add_pre_commit_config_file()

#         # Assert
#         out, _ = capfd.readouterr()
#         assert out == ""
#         assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == ""


class TestRemovePreCommitConfig:
    def test_exists(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Removing .pre-commit-config.yaml file.\n"

    def test_already_missing(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_does_not_exist(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()


class TestInstallPreCommitHooks:
    def test_message(
        self,
        uv_init_dir: Path,
        capfd: pytest.CaptureFixture[str],
        vary_network_conn: None,
    ):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pre-commit"], "dev")
            add_placeholder_hook()
            capfd.readouterr()

            # Act
            install_pre_commit_hooks()

            # Assert
            output = capfd.readouterr().out
            assert output == "✔ Ensuring pre-commit hooks are installed.\n"

    def test_err(self, tmp_path: Path):
        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(PreCommitInstallationError):
            # Will fail because pre-commit isn't installed.
            install_pre_commit_hooks()


class TestUninstallPreCommitHooks:
    def test_message_and_file(
        self,
        uv_init_dir: Path,
        capfd: pytest.CaptureFixture[str],
        vary_network_conn: None,
    ):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pre-commit"], "dev")
            add_placeholder_hook()
            capfd.readouterr()

            # Act
            uninstall_pre_commit_hooks()

            # Assert
            output = capfd.readouterr().out
            assert output == "✔ Ensuring pre-commit hooks are uninstalled.\n"

        # Uninstalling the hooks shouldn't remove the config file
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_err(self, tmp_path: Path):
        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(PreCommitInstallationError):
            # Will fail because pre-commit isn't installed.
            uninstall_pre_commit_hooks()
