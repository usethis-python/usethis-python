from pathlib import Path

import pytest
from packaging.specifiers import SpecifierSet

from usethis._integrations.pyproject.io_ import PyProjectTOMLNotFoundError
from usethis._integrations.pyproject.requires_python import get_requires_python
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
        with change_cwd(tmp_path):
            requires_python = get_requires_python()

        # Assert
        assert requires_python == SpecifierSet(">=3.7")

    def test_no_pyproject(self, tmp_path: Path):
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            get_requires_python()
