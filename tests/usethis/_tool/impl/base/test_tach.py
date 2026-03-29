from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.base.tach import TachTool


class TestTachTool:
    class TestPrintHowToUse:
        def test_pre_commit_and_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / "uv.lock").touch()
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: tach
        name: tach
        entry: uv run --frozen --offline tach check
""")

            # Act
            with change_cwd(tmp_path), files_manager():
                TachTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'uv run pre-commit run -a tach' to run Tach.\n")

        def test_pre_commit_no_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: tach
        name: tach
        entry: uv run --frozen --offline tach check
""")

            # Act
            with change_cwd(tmp_path), files_manager():
                TachTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'pre-commit run -a tach' to run Tach.\n")

        def test_uv_only(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                TachTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'uv run tach check' to run Tach.\n")

        def test_basic(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with change_cwd(tmp_path), files_manager():
                TachTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'tach check' to run Tach.\n")

    class TestIsUsed:
        def test_not_used_empty_dir(self, tmp_path: Path):
            with change_cwd(tmp_path), files_manager():
                assert not TachTool().is_used()

        def test_used_when_tach_toml_exists(self, tmp_path: Path):
            (tmp_path / "tach.toml").write_text('source_roots = ["src"]\n')
            with change_cwd(tmp_path), files_manager():
                assert TachTool().is_used()

    class TestAddConfig:
        def test_creates_tach_toml(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                TachTool().add_configs()

            # Assert
            assert (tmp_path / "tach.toml").exists()

    class TestGetConfigSpec:
        def test_empty_src_directory(self, tmp_path: Path):
            # Arrange: Create empty src directory with package subdirectory
            (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypkg"')
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "mypkg").mkdir()

            # Act: config_spec should not crash
            with change_cwd(tmp_path), files_manager():
                config_spec = TachTool().config_spec()

            # Assert: Should return a valid config spec
            assert config_spec is not None
            assert len(config_spec.config_items) > 0

        def test_with_real_package_layers(self, tmp_path: Path):
            """Test config_spec with a package that has enough modules to produce layers."""
            # Arrange
            (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypkg"')
            pkg_dir = tmp_path / "src" / "mypkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "__init__.py").touch()
            # Create modules: c imports b, b imports a, a has no imports
            (pkg_dir / "a.py").write_text("")
            (pkg_dir / "b.py").write_text("from mypkg import a\n")
            (pkg_dir / "c.py").write_text("from mypkg import b\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                config_spec = TachTool().config_spec()

            # Assert: Should have layers and modules config items
            assert config_spec is not None
            descriptions = [item.description for item in config_spec.config_items]
            assert "Layers" in descriptions
            assert "Modules" in descriptions

        def test_with_version_module_excluded(self, tmp_path: Path):
            """Test that _version module is excluded as utility."""
            # Arrange
            (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypkg"')
            pkg_dir = tmp_path / "src" / "mypkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "__init__.py").touch()
            (pkg_dir / "a.py").write_text("")
            (pkg_dir / "b.py").write_text("")
            (pkg_dir / "c.py").write_text("")
            (pkg_dir / "_version.py").write_text('__version__ = "0.1.0"\n')

            # Act
            with change_cwd(tmp_path), files_manager():
                config_spec = TachTool().config_spec()

            # Assert: config_spec should be valid
            assert config_spec is not None
            # Check that modules section exists
            descriptions = [item.description for item in config_spec.config_items]
            assert "Modules" in descriptions

            # Verify _version appears as utility
            modules_item = next(
                item
                for item in config_spec.config_items
                if item.description == "Modules"
            )
            modules_entry = modules_item.root[Path("tach.toml")]
            modules_data = modules_entry.get_value()
            assert isinstance(modules_data, list)
            utility_paths = [
                m["path"] for m in modules_data if m.get("utility") is True
            ]
            assert "mypkg._version" in utility_paths
