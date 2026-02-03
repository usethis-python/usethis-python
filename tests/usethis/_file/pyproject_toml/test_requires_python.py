from pathlib import Path

import pytest
from packaging.specifiers import SpecifierSet

from usethis._file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
    get_requires_python,
)
from usethis._python.version import PythonVersion
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
        with change_cwd(tmp_path), PyprojectTOMLManager():
            requires_python = get_requires_python()

        # Assert
        assert requires_python == SpecifierSet(">=3.7")

    def test_no_pyproject_toml(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(PyprojectTOMLNotFoundError),
        ):
            get_requires_python()


class TestGetRequiredMinorPythonVersions:
    def test_simple_lower_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.10"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - unbounded upward should extend to hard-coded limit
        assert len(versions) == 6
        assert versions[0] == PythonVersion(major="3", minor="10", patch=None)
        # N.B. this needs maintenance as new versions are released
        assert versions[-1] == PythonVersion(major="3", minor="15", patch=None)
        assert all(v.major == "3" for v in versions)
        assert all(int(v.minor) >= 10 for v in versions)

    def test_upper_and_lower_bounds(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.10,<3.13"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert
        assert versions == [
            PythonVersion(major="3", minor="10", patch=None),
            PythonVersion(major="3", minor="11", patch=None),
            PythonVersion(major="3", minor="12", patch=None),
        ]

    def test_exact_version(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = "==3.11"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert
        assert versions == [PythonVersion(major="3", minor="11", patch=None)]

    def test_patch_versions_in_specifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.10.5,<3.12.0"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - 3.10 represents 3.10.* which includes 3.10.5+
        # Minor versions are treated hierarchically, not as .0
        assert versions == [
            PythonVersion(major="3", minor="10", patch=None),
            PythonVersion(major="3", minor="11", patch=None),
        ]

    def test_cross_major_version(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=2.7,<4.0"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - should include Python 2.7, 3.x versions
        assert len(versions) > 0
        assert versions[0].major == "2"
        assert any(v.major == "3" for v in versions)
        # Should not include 4.x
        assert not any(v.major == "4" for v in versions)

    def test_less_than_or_equal(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.8,<=3.11"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert
        assert versions == [
            PythonVersion(major="3", minor="8", patch=None),
            PythonVersion(major="3", minor="9", patch=None),
            PythonVersion(major="3", minor="10", patch=None),
            PythonVersion(major="3", minor="11", patch=None),
        ]

    def test_no_pyproject_toml(self, tmp_path: Path):
        # Act & Assert
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(PyprojectTOMLNotFoundError),
        ):
            get_required_minor_python_versions()

    def test_missing_requires_python(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
"""
        )

        # Act & Assert
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(MissingRequiresPythonError),
        ):
            get_required_minor_python_versions()

    def test_complex_constraint(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.9,!=3.10,<3.13"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - !=3.10 only excludes 3.10.0, but 3.10.5+ are valid
        # So 3.10 is included hierarchically (some patches satisfy)
        assert versions == [
            PythonVersion(major="3", minor="9", patch=None),
            PythonVersion(major="3", minor="10", patch=None),
            PythonVersion(major="3", minor="11", patch=None),
            PythonVersion(major="3", minor="12", patch=None),
        ]

    def test_empty_result(self, tmp_path: Path):
        # Arrange - impossible constraint
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">3.10,<3.10"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert
        assert versions == []

    def test_unbounded_downward(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = "<3.12"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - unbounded downward should extend to hard-coded limit (3.0)
        assert versions[0] == PythonVersion(major="3", minor="0", patch=None)
        assert versions[-1] == PythonVersion(major="3", minor="11", patch=None)
        assert all(v.major == "3" for v in versions)
        assert len(versions) == 12  # 3.0 through 3.11

    def test_python_2_range(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=2.7"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - should cap at 2.7 for Python 2
        assert all(v.major == "2" for v in versions)
        assert versions == [PythonVersion(major="2", minor="7", patch=None)]

    def test_python_4_upper_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.6,<4.0"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            versions = get_required_minor_python_versions()

        # Assert - should include all 3.x up to hard-coded limit
        assert versions[0] == PythonVersion(major="3", minor="6", patch=None)
        assert versions[-1] == PythonVersion(major="3", minor="15", patch=None)
        assert all(v.major == "3" for v in versions)
