from pathlib import Path

import pytest

from usethis._integrations.uv.init import ensure_pyproject_toml
from usethis._test import change_cwd


class TestEnsurePyprojectTOML:
    def test_created(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "pyproject.toml").exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Writing 'pyproject.toml'.\n"

    def test_already_exists_unchanged(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("test")

        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == "test"
        out, err = capfd.readouterr()
        assert not err
        assert not out

    def test_hello_py_respected(self, tmp_path: Path):
        # Arrange
        (tmp_path / "hello.py").write_text("test")

        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "hello.py").exists()
        assert (tmp_path / "hello.py").read_text() == "test"

    def test_no_hello_py_created(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / "hello.py").exists()

    def test_no_readme(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / "README.md").exists()

    def test_no_pin_python(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / ".python-version").exists()

    def test_no_vcs(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / ".git").exists()
