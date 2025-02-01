from pathlib import Path

import pytest

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLDecodeError,
    PyProjectTOMLNotFoundError,
)
from usethis._integrations.pyproject.io_ import read_pyproject_toml
from usethis._test import change_cwd


class TestReadPyprojectTOML:
    def test_empty(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.touch()

        # Act
        with change_cwd(tmp_path):
            result = read_pyproject_toml().value

        # Assert
        assert result == {}

    def test_single_map(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.write_text('name = "usethis"')

        # Act
        with change_cwd(tmp_path):
            result = read_pyproject_toml().value

        # Assert
        assert result == {"name": "usethis"}

    def test_invalid_toml(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.write_text("name =")

        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLDecodeError):
            read_pyproject_toml().value

    def test_missing(self, tmp_path: Path):
        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            read_pyproject_toml().value
