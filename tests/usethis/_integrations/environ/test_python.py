from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._integrations.environ.python import get_supported_minor_python_versions
from usethis._integrations.python.version import PythonVersion
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum


class TestGetSupportedMinorPythonVersions:
    class TestNoneBackend:
        def test_with_requires_python_range(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str], monkeypatch
        ):
            # Arrange

            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / "pyproject.toml").write_text(
                """
[project]
requires-python = ">=3.11,<3.13"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert
            assert versions == [
                PythonVersion(major="3", minor="11", patch=None),
                PythonVersion(major="3", minor="12", patch=None),
            ]
            # Current interpreter is 3.10, outside the range
            out, _err = capfd.readouterr()
            assert "Current Python interpreter" in out
            assert "outside requires-python bounds" in out

        def test_with_single_version(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange

            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            monkeypatch.setattr(
                "usethis._integrations.python.version.PythonVersion.from_interpreter",
                lambda: PythonVersion(major="3", minor="10", patch=None),
            )
            (tmp_path / "pyproject.toml").write_text(
                """
[project]
requires-python = ">=3.13"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should get all versions from 3.13 onwards
            assert len(versions) > 0
            assert versions[0] == PythonVersion(major="3", minor="13", patch=None)
            assert all(v.major == "3" for v in versions)
            assert all(int(v.minor) >= 13 for v in versions)
            out, _err = capfd.readouterr()
            assert "Current Python interpreter" in out
            assert "outside requires-python bounds" in out

        def test_no_pyproject_toml(self, tmp_path: Path, monkeypatch):
            # Arrange

            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should return current interpreter version
            current = PythonVersion.from_interpreter()
            assert versions == [current]

        def test_no_requires_python(self, tmp_path: Path, monkeypatch):
            # Arrange

            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / "pyproject.toml").write_text(
                """
[project]
name = "test"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should return current interpreter version
            current = PythonVersion.from_interpreter()
            assert versions == [current]
