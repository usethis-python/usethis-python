from pathlib import Path

import pytest

from usethis._integrations.pyproject.errors import PyProjectTOMLNotFoundError
from usethis._integrations.pyproject.requires_python import MissingRequiresPythonError
from usethis._integrations.uv.python import get_supported_major_python_versions
from usethis._test import change_cwd


class TestGetSupportedMajorPythonVersions:
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
            supported_major_python = get_supported_major_python_versions()

        # Assert
        assert supported_major_python == [7, 8, 9, 10, 11, 12, 13]

    def test_upper_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.9,<3.12"
"""
        )

        # Act
        with change_cwd(tmp_path):
            supported_major_python = get_supported_major_python_versions()

        # Assert
        assert supported_major_python == [9, 10, 11]

    def test_no_pyproject(self, tmp_path: Path):
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            get_supported_major_python_versions()

    def test_no_requires_python(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "foo"
"""
        )

        # Act
        with change_cwd(tmp_path), pytest.raises(MissingRequiresPythonError):
            get_supported_major_python_versions()
