from pathlib import Path

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.base.pytest import PytestTool
from usethis._types.backend import BackendEnum


class TestPytestTool:
    class TestDefaultCommand:
        def test_uv_backend_with_uv_lock(self, tmp_path: Path):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = PytestTool().how_to_use_cmd()

            # Assert
            assert cmd == "uv run pytest"

        def test_uv_backend_without_uv_lock(self, tmp_path: Path):
            # Arrange - no uv.lock file

            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = PytestTool().how_to_use_cmd()

            # Assert
            assert cmd == "pytest"

        def test_none_backend(self, tmp_path: Path):
            # Arrange

            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                cmd = PytestTool().how_to_use_cmd()

            # Assert
            assert cmd == "pytest"

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect pytest.ini to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                PytestTool().add_configs()

            # Assert
            assert (tmp_path / "pytest.ini").exists()
            assert not (tmp_path / "pyproject.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                PytestTool().add_configs()

            # Assert
            assert not (tmp_path / "pytest.ini").exists()
            assert (tmp_path / "pyproject.toml").exists()
