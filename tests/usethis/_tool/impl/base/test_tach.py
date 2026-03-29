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
