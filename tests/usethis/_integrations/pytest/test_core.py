from pathlib import Path

import pytest

from _test import change_cwd
from usethis._integrations.pytest.core import (
    add_example_test,
    add_pytest_dir,
    remove_pytest_dir,
)


class TestAddPytestDir:
    def test_exists(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            add_pytest_dir()

        # Assert
        assert (tmp_path / "tests").exists()

    def test_message(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            add_pytest_dir()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Creating '/tests'.\n✔ Writing '/tests/conftest.py'.\n"

    def test_conftest_exists(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_pytest_dir()

        # Assert
        assert (tmp_path / "tests" / "conftest.py").exists()
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '/tests/conftest.py'.\n"

    def test_conftest_already_exists(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "conftest.py").write_text("existing")

        # Act
        with change_cwd(tmp_path):
            add_pytest_dir()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert (tmp_path / "tests" / "conftest.py").read_text() == "existing"

    def test_uses_test_dir_when_exists(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange: 'test' directory already exists
        (tmp_path / "test").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_pytest_dir()

        # Assert: conftest.py is created in 'test/', not 'tests/'
        assert (tmp_path / "test" / "conftest.py").exists()
        assert not (tmp_path / "tests").exists()
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '/test/conftest.py'.\n"


class TestAddExampleTest:
    def test_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_example_test()

        # Assert
        assert (tmp_path / "tests" / "test_example.py").exists()

    def test_content(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_example_test()

        # Assert
        content = (tmp_path / "tests" / "test_example.py").read_text()
        assert "def test_add():" in content
        assert "assert 1 + 1 == 2" in content
        assert "An example test - replace with your own tests!" in content

    def test_message(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_example_test()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '/tests/test_example.py'.\n"

    def test_already_exists(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_example.py").write_text("existing content")

        # Act
        with change_cwd(tmp_path):
            add_example_test()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert (
            tmp_path / "tests" / "test_example.py"
        ).read_text() == "existing content"

    def test_uses_test_dir_when_exists(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange: 'test' directory already exists
        (tmp_path / "test").mkdir()

        # Act
        with change_cwd(tmp_path):
            add_example_test()

        # Assert: example test is placed in 'test/', not 'tests/'
        assert (tmp_path / "test" / "test_example.py").exists()
        assert not (tmp_path / "tests").exists()
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '/test/test_example.py'.\n"


class TestRemovePytestDir:
    def test_blank_slate(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        # Assert
        assert not (tmp_path / "tests").exists()

    def test_dir(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()

        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        # Assert
        assert not (tmp_path / "tests").exists()

    def test_protect_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_something.py").touch()

        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        # Assert
        assert (tmp_path / "tests").exists()
        assert (tmp_path / "tests" / "test_something.py").exists()

    def test_roundtrip(self, tmp_path: Path):
        with change_cwd(tmp_path):
            # Arrange
            add_pytest_dir()

            # Act
            remove_pytest_dir()

        # Assert
        assert not (tmp_path / "tests").exists()

    def test_roundtrip_with_example(self, tmp_path: Path):
        with change_cwd(tmp_path):
            # Arrange
            add_pytest_dir()
            add_example_test()

            # Act
            remove_pytest_dir()

        # Assert
        assert not (tmp_path / "tests").exists()

    def test_only_example_test(self, tmp_path: Path):
        # Arrange
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_example.py").touch()

        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        # Assert
        assert not (tmp_path / "tests").exists()

    def test_removes_test_dir_when_exists(self, tmp_path: Path):
        # Arrange: 'test' directory exists with only managed files
        (tmp_path / "test").mkdir()
        (tmp_path / "test" / "conftest.py").touch()

        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        # Assert: 'test/' is removed, not 'tests/'
        assert not (tmp_path / "test").exists()
        assert not (tmp_path / "tests").exists()

    def test_protects_test_dir_with_user_files(self, tmp_path: Path):
        # Arrange: 'test' directory exists with user files
        (tmp_path / "test").mkdir()
        (tmp_path / "test" / "test_something.py").touch()

        # Act
        with change_cwd(tmp_path):
            remove_pytest_dir()

        assert (tmp_path / "test").exists()
