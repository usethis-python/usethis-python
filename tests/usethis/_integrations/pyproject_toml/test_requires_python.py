from pathlib import Path

import pytest
from packaging.specifiers import SpecifierSet

from usethis._integrations.pyproject_toml.io_ import (
    PyprojectTOMLNotFoundError,
    pyproject_toml_io_manager,
)
from usethis._integrations.pyproject_toml.requires_python import get_requires_python
from usethis._test import change_cwd


class TestGetRequiresPython:
    def test_lower_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.7"
"""
        )

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            requires_python = get_requires_python()

        # Assert
        assert requires_python == SpecifierSet(">=3.7")

    def test_no_pyproject(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            pyproject_toml_io_manager.open(),
            pytest.raises(PyprojectTOMLNotFoundError),
        ):
            get_requires_python()
