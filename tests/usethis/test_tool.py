from pathlib import Path

import pytest

from usethis._integrations.pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._integrations.pre_commit.hooks import get_hook_names
from usethis._integrations.pyproject.config import PyProjectConfig
from usethis._integrations.pyproject.core import set_config_value
from usethis._integrations.uv.deps import add_deps_to_group
from usethis._test import change_cwd
from usethis._tool import Tool


class DefaultTool(Tool):
    """An example tool for testing purposes.

    This tool has minimal non-default configuration.
    """

    @property
    def name(self) -> str:
        return "default_tool"


class MyTool(Tool):
    """An example tool for testing purposes.

    This tool has maximal non-default configuration.
    """

    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def dev_deps(self) -> list[str]:
        return [self.name, "black", "flake8"]

    def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
        return [
            PreCommitRepoConfig(
                repo=f"repo for {self.name}", hooks=[HookConfig(id="deptry")]
            )
        ]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(id_keys=["tool", self.name], main_contents={"key": "value"})
        ]

    def get_associated_ruff_rules(self) -> list[str]:
        return ["MYRULE"]

    def get_unique_dev_deps(self) -> list[str]:
        return [self.name, "isort"]  # Obviously "isort" is not mytool's! For testing.

    def get_managed_files(self) -> list[Path]:
        return [Path("mytool-config.yaml")]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", self.name], ["project", "classifiers"]]


class TestTool:
    class TestName:
        def test_default(self):
            tool = DefaultTool()
            assert tool.name == "default_tool"

        def test_specific(self):
            tool = MyTool()
            assert tool.name == "my_tool"

    class TestDevDeps:
        def test_default(self):
            tool = DefaultTool()
            assert tool.dev_deps == []

        def test_specific(self):
            tool = MyTool()
            assert tool.dev_deps == ["my_tool", "black", "flake8"]

    class TestGetPreCommitRepoConfigs:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_pre_commit_repo_configs() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_pre_commit_repo_configs() == [
                PreCommitRepoConfig(
                    repo="repo for my_tool", hooks=[HookConfig(id="deptry")]
                )
            ]

    class TestGetPyprojectConfigs:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_pyproject_configs() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_pyproject_configs() == [
                PyProjectConfig(
                    id_keys=["tool", "my_tool"], main_contents={"key": "value"}
                )
            ]

    class TestGetAssociatedRuffRules:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_associated_ruff_rules() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_associated_ruff_rules() == ["MYRULE"]

    class TestGetUniqueDevDeps:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_unique_dev_deps() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_unique_dev_deps() == ["my_tool", "isort"]

    class TestGetManagedFiles:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_managed_files() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_managed_files() == [
                Path("mytool-config.yaml"),
            ]

    class TestGetPyprojectIdKeys:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_pyproject_id_keys() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_pyproject_id_keys() == [
                ["tool", "my_tool"],
                ["project", "classifiers"],
            ]

    class TestIsUsed:
        def test_some_deps(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                add_deps_to_group(["isort"], "eggs")

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_non_managed_deps(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                add_deps_to_group(["black"], "eggs")
                # Act
                result = tool.is_used()

            # Assert
            assert not result

        def test_files(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                Path("mytool-config.yaml").touch()

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_dir(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                Path("mytool-config.yaml").mkdir()

                # Act
                result = tool.is_used()

            # Assert
            assert not result

        def test_pyproject(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                set_config_value(["tool", "my_tool", "key"], "value")

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_empty(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(uv_init_dir):
                result = tool.is_used()

            # Assert
            assert not result

    class TestAddPreCommitRepoConfigs:
        def test_no_repo_configs(self, tmp_path: Path):
            # Arrange
            class NoRepoConfigsTool(Tool):
                @property
                def name(self) -> str:
                    return "no_repo_configs_tool"

                def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
                    return []

            nrc_tool = NoRepoConfigsTool()

            # Act
            with change_cwd(tmp_path):
                nrc_tool.add_pre_commit_repo_configs()

                # Assert
                assert not (tmp_path / ".pre-commit-config.yaml").exists()

        # TODO test multiple pre-commit configs

        def test_file_created(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(tmp_path):
                tool.add_pre_commit_repo_configs()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()

        def test_file_not_created(self, tmp_path: Path):
            # Arrange
            tool = DefaultTool()

            # Act
            with change_cwd(tmp_path):
                tool.add_pre_commit_repo_configs()

                # Assert
                assert not (tmp_path / ".pre-commit-config.yaml").exists()

        def test_add_successful(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(tmp_path):
                tool.add_pre_commit_repo_configs()

                # Assert
                output = capfd.readouterr().out
                assert output == (
                    "✔ Writing '.pre-commit-config.yaml'.\n"
                    "✔ Adding hook 'validate-pyproject' to '.pre-commit-config.yaml'.\n"
                )
                assert "deptry" in get_hook_names()

    class TestRemovePreCommitRepoConfigs: ...  # TODO
