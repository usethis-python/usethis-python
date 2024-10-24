from pathlib import Path
from typing import Any, Literal

import pytest
import requests
from packaging.specifiers import SpecifierSet

from usethis._integrations.pyproject.io import PyProjectTOMLNotFoundError
from usethis._integrations.pyproject.requires_python import (
    MAX_MAJOR_PY3,
    MissingRequiresPythonError,
    get_requires_python,
    get_supported_major_python_versions,
)
from usethis._utils._test import change_cwd


class TestMaxMajorPy3:
    def test_max_major_py3(self):
        try:
            endoflife_info: list[dict[str, Any] | dict[Literal["cycle"], str]] = (
                requests.get(
                    r"https://endoflife.date/api/python.json", timeout=5
                ).json()
            )
        except requests.exceptions.ConnectionError:
            pytest.skip(reason="Failed to connect to https://endoflife.date/")

        assert (
            max(int(x["cycle"].split(".")[1]) for x in endoflife_info) == MAX_MAJOR_PY3
        )


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
