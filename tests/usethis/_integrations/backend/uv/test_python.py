from pathlib import Path

from usethis._integrations.backend.uv.python import (
    _parse_python_version_from_uv_output,
    get_available_uv_python_versions,
    get_supported_uv_minor_python_versions,
)
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.python.version import PythonVersion
from usethis._test import change_cwd


class TestGetAvailableUVPythonVersions:
    def test_nonempty(self):
        # Act
        results = get_available_uv_python_versions()

        # Assert
        assert results


class TestGetSupportedUVMinorPythonVersions:
    def test_lower_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.10,<3.12"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            supported_python = get_supported_uv_minor_python_versions()

        # Assert
        assert [v.minor for v in supported_python] == ["10", "11"]
        assert all(v.patch is None for v in supported_python)

    def test_upper_bound(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.9,<3.12"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            supported_python = get_supported_uv_minor_python_versions()

        # Assert
        assert [v.minor for v in supported_python] == ["9", "10", "11"]
        assert all(v.patch is None for v in supported_python)

    def test_no_pyproject_toml(self, tmp_path: Path):
        with change_cwd(tmp_path), PyprojectTOMLManager():
            result = get_supported_uv_minor_python_versions()
            current_version = PythonVersion.from_interpreter()
            assert len(result) == 1
            assert result[0].major == current_version.major
            assert result[0].minor == current_version.minor
            assert result[0].patch is None

    def test_no_requires_python(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "foo"
"""
        )

        # Act
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
        ):
            versions = get_supported_uv_minor_python_versions()

        # Assert
        current_version = PythonVersion.from_interpreter()
        assert len(versions) == 1
        assert versions[0].major == current_version.major
        assert versions[0].minor == current_version.minor
        assert versions[0].patch is None


class TestParsePythonVersionFromUVOutput:
    def test_alpha(self):
        # Arrange
        version = "cpython-3.14.0a3+freethreaded-linux-x86_64-gnu"

        # Act
        minor_version = _parse_python_version_from_uv_output(version)

        # Assert
        assert minor_version == "3.14.0a3"
