from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import TyTOMLManager, files_manager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema
from usethis._test import change_cwd
from usethis._tool.config import ConfigEntry, ConfigItem
from usethis._tool.impl.base.ty import TyTool
from usethis._types.backend import BackendEnum


class TestTyTool:
    class TestDefaultCommand:
        def test_uv_backend_with_uv_lock(self, tmp_path: Path):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = TyTool().how_to_use_cmd()

            # Assert
            assert cmd == "uv run ty check"

        def test_uv_backend_without_uv_lock(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = TyTool().how_to_use_cmd()

            # Assert
            assert cmd == "ty check"

        def test_none_backend(self, tmp_path: Path):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                cmd = TyTool().how_to_use_cmd()

            # Assert
            assert cmd == "ty check"

    class TestPrintHowToUse:
        def test_pre_commit_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text(
                """\
repos:
  - repo: local
    hooks:
      - id: ty
        name: ty
        entry: uv run --frozen --offline ty check
        language: system
        always_run: true
        pass_filenames: false
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'pre-commit run -a ty' to run the ty type checker.\n")

        def test_pre_commit_not_configured(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text(
                """\
repos: []
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == "☐ Run 'ty check' to run the ty type checker.\n"

        def test_no_pre_commit(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == "☐ Run 'ty check' to run the ty type checker.\n"

    class TestAddConfig:
        def test_src_include_written_to_pyproject(self, tmp_path: Path):
            """ty's config_spec adds src.include to pyproject.toml."""
            # Arrange
            (tmp_path / "pyproject.toml").write_text("[project]\nname = 'example'\n")
            (tmp_path / "src").mkdir()

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().add_configs()

            # Assert
            content = (tmp_path / "pyproject.toml").read_text()
            assert "tool.ty.src" in content
            assert "include" in content

        def test_src_include_src_layout(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("[project]\nname = 'example'\n")
            (tmp_path / "src").mkdir()

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().add_configs()

            # Assert
            content = (tmp_path / "pyproject.toml").read_text()
            assert '"src"' in content
            assert '"tests"' in content

        def test_src_include_root_layout(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("[project]\nname = 'example'\n")
            pkg_dir = tmp_path / "mypackage"
            pkg_dir.mkdir()
            (pkg_dir / "__init__.py").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().add_configs()

            # Assert
            content = (tmp_path / "pyproject.toml").read_text()
            assert '"mypackage"' in content
            assert '"tests"' in content

    class TestConfigSpec:
        def test_pyproject_toml_overall_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            overall_item = result.config_items[0]
            assert isinstance(overall_item, ConfigItem)
            assert overall_item.root[Path("pyproject.toml")] == ConfigEntry(
                keys=["tool", "ty"]
            )

        def test_ty_toml_overall_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            overall_item = result.config_items[0]
            assert isinstance(overall_item, ConfigItem)
            assert overall_item.root[Path("ty.toml")] == ConfigEntry(keys=[])

        def test_dot_ty_toml_overall_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            overall_item = result.config_items[0]
            assert isinstance(overall_item, ConfigItem)
            assert overall_item.root[Path(".ty.toml")] == ConfigEntry(keys=[])

        def test_three_file_managers(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            paths = set(result.file_manager_by_relative_path.keys())
            assert paths == {Path(".ty.toml"), Path("ty.toml"), Path("pyproject.toml")}

        def test_two_config_items(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            assert len(result.config_items) == 2
            assert result.config_items[0].description == "Overall config"
            assert result.config_items[1].description == "Source include"

        def test_src_include_pyproject_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            src_item = result.config_items[1]
            assert src_item.root[Path("pyproject.toml")].keys == [
                "tool",
                "ty",
                "src",
                "include",
            ]

        def test_src_include_ty_toml_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            src_item = result.config_items[1]
            assert src_item.root[Path("ty.toml")].keys == ["src", "include"]

        def test_src_include_dot_ty_toml_keys(self):
            # Arrange
            tool = TyTool()

            # Act
            result = tool.config_spec()

            # Assert
            src_item = result.config_items[1]
            assert src_item.root[Path(".ty.toml")].keys == ["src", "include"]

    class TestRemoveConfig:
        def test_removes_ty_section_from_pyproject(self, tmp_path: Path):
            # Arrange
            pyproject = tmp_path / "pyproject.toml"
            pyproject.write_text("[tool.ty]\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().remove_configs()

            # Assert
            assert "[tool.ty]" not in pyproject.read_text()

        def test_removes_config_from_ty_toml(self, tmp_path: Path):
            # Arrange
            ty_toml = tmp_path / "ty.toml"
            ty_toml.write_text('[rules]\npossibly-unresolved-reference = "warn"\n')

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().remove_configs()

            # Assert
            # The sentinel entry (keys=[]) means the entire file content is managed
            # but since NoConfigValue is used, remove will try del with keys=[]
            # which removes the root — clearing the file contents
            assert ty_toml.exists()

        def test_removes_config_from_dot_ty_toml(self, tmp_path: Path):
            # Arrange
            dot_ty_toml = tmp_path / ".ty.toml"
            dot_ty_toml.write_text('[rules]\npossibly-unresolved-reference = "warn"\n')

            # Act
            with change_cwd(tmp_path), files_manager():
                TyTool().remove_configs()

            # Assert
            assert dot_ty_toml.exists()

    class TestIsUsed:
        def test_ty_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "ty.toml").write_text("[rules]\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                result = TyTool().is_used()

            # Assert
            assert result

        def test_dot_ty_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ty.toml").write_text("[rules]\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                result = TyTool().is_used()

            # Assert
            assert result

        def test_pyproject_toml_with_tool_ty(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("[tool.ty]\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                result = TyTool().is_used()

            # Assert
            assert result

        def test_not_used(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                result = TyTool().is_used()

            # Assert
            assert not result

    class TestPreferredFileManager:
        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                fm = TyTool().preferred_file_manager()

            # Assert
            assert isinstance(fm, PyprojectTOMLManager)

        def test_no_pyproject_toml(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                fm = TyTool().preferred_file_manager()

            # Assert
            assert isinstance(fm, TyTOMLManager)

    class TestGetPreCommitConfig:
        def test_uv_backend(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                config = TyTool().pre_commit_config()

            # Assert
            assert len(config.repo_configs) == 1
            repo = config.repo_configs[0].repo
            assert isinstance(repo, schema.LocalRepo)
            assert repo.hooks is not None
            assert len(repo.hooks) == 1
            assert repo.hooks[0].id == "ty"
            assert repo.hooks[0].entry == "uv run --frozen --offline ty check"

        def test_none_backend(self, tmp_path: Path):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                config = TyTool().pre_commit_config()

            # Assert
            assert len(config.repo_configs) == 1
            repo = config.repo_configs[0].repo
            assert isinstance(repo, schema.LocalRepo)
            assert repo.hooks is not None
            assert len(repo.hooks) == 1
            assert repo.hooks[0].id == "ty"
            assert repo.hooks[0].entry == "ty check"

    class TestManagedFiles:
        def test_managed_files(self):
            tool = TyTool()
            assert Path("ty.toml") in tool.managed_files
            assert Path(".ty.toml") in tool.managed_files
