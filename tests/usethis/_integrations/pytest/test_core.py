from pathlib import Path

import pytest

from usethis._integrations.pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._utils._test import change_cwd


class TestAddPytestDir:
    def test_exists(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            add_pytest_dir()

        # Assert
        assert (uv_init_dir / "tests").exists()

    def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            add_pytest_dir()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Creating '/tests'.\n✔ Writing '/tests/conftest.py'.\n"

    def test_conftest_exists(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (uv_init_dir / "tests").mkdir()

        # Act
        with change_cwd(uv_init_dir):
            add_pytest_dir()

        # Assert
        assert (uv_init_dir / "tests" / "conftest.py").exists()
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '/tests/conftest.py'.\n"


class TestRemovePytestDir:
    def test_blank_slate(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            remove_pytest_dir()

        # Assert
        assert not (uv_init_dir / "tests").exists()

    def test_dir(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "tests").mkdir()

        # Act
        with change_cwd(uv_init_dir):
            remove_pytest_dir()

        # Assert
        assert not (uv_init_dir / "tests").exists()

    def test_protect_file(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "tests").mkdir()
        (uv_init_dir / "tests" / "test_something.py").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pytest_dir()

        # Assert
        assert (uv_init_dir / "tests").exists()
        assert (uv_init_dir / "tests" / "test_something.py").exists()

    def test_roundtrip(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir):
            # Arrange
            add_pytest_dir()

            # Act
            remove_pytest_dir()

        # Assert
        assert not (uv_init_dir / "tests").exists()
