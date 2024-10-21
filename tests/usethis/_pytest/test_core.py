from pathlib import Path

import pytest

from usethis._pytest.core import add_pytest_dir
from usethis._test import change_cwd


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
