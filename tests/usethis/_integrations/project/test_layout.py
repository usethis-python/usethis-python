from pathlib import Path

from _test import change_cwd
from usethis._integrations.project.layout import get_source_dir_str, get_tests_dir_str


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


class TestGetTestsDirStr:
    def test_tests_dir_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "tests"

    def test_test_dir_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "test").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "test"

    def test_neither_exists_defaults_to_tests(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "tests"

    def test_tests_preferred_over_test(self, tmp_path: Path):
        # Arrange: both directories exist - 'tests' should be preferred
        (tmp_path / "tests").mkdir()
        (tmp_path / "test").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "tests"

    def test_test_file_not_dir(self, tmp_path: Path):
        # Arrange: 'test' exists as a file, not a directory
        (tmp_path / "test").touch()

        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "tests"

    def test_tests_file_not_dir(self, tmp_path: Path):
        # Arrange: 'tests' exists as a file, not a directory; 'test' exists as a dir
        (tmp_path / "tests").touch()
        (tmp_path / "test").mkdir()

        # Act
        with change_cwd(tmp_path):
            result = get_tests_dir_str()

        # Assert
        assert result == "test"
