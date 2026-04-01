from pathlib import Path

from usethis._backend.poetry.detect import is_poetry_used
from usethis._config_file import files_manager
from usethis._test import change_cwd


class TestIsPoetryUsed:
    def test_empty_dir(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_poetry_used()

        # Assert
        assert not result

    def test_poetry_lock(self, tmp_path: Path):
        # Arrange
        (tmp_path / "poetry.lock").touch()

        # Act
        with change_cwd(tmp_path):
            result = is_poetry_used()

        # Assert
        assert result

    def test_poetry_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "poetry.toml").touch()

        # Act
        with change_cwd(tmp_path):
            result = is_poetry_used()

        # Assert
        assert result

    def test_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry]
name = "test"
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_poetry_used()

        # Assert
        assert result
