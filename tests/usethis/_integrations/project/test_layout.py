from pathlib import Path

from _test import change_cwd
from usethis._integrations.project.layout import get_source_dir_str


class TestGetSourceDirStr:
    def test_has_src(self, tmp_path: Path):
        # Arrange
        (tmp_path / "src").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_source_dir_str()

        # Assert
        assert result == "src"

    def test_no_src(self, tmp_path: Path):
        # Arrange
        (tmp_path / "foo").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_source_dir_str()

        # Assert
        assert result == "."

    def test_src_file_not_dir(self, tmp_path: Path):
        # Arrange
        (tmp_path / "src").touch()

        # Act
        with change_cwd(tmp_path):
            result = get_source_dir_str()

        # Assert
        assert result == "."

    def test_setup_py_present(self, tmp_path: Path):
        # Arrange
        (tmp_path / "setup.py").touch()

        # Act
        with change_cwd(tmp_path):
            result = get_source_dir_str()

        # Assert
        assert result == "."
