from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._file.pyproject_toml.requires_python import MissingRequiresPythonError
from usethis._integrations.environ.python import get_supported_minor_python_versions
from usethis._python.version import PythonVersion
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum


class TestGetSupportedMinorPythonVersions:
    class TestNoneBackend:
        def test_with_requires_python_range(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange

            monkeypatch.setattr(
                "usethis._backend.dispatch.get_backend",
                lambda: BackendEnum.none,
            )
            monkeypatch.setattr(
                "usethis._python.version.PythonVersion.from_interpreter",
                lambda: PythonVersion(major="3", minor="10", patch=None),
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
            assert "Current Python version" in out
            assert "outside requires-python bounds" in out

        def test_with_single_version(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange

            monkeypatch.setattr(
                "usethis._backend.dispatch.get_backend",
                lambda: BackendEnum.none,
            )
            monkeypatch.setattr(
                "usethis._python.version.PythonVersion.from_interpreter",
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
            assert "Current Python version" in out
            assert "outside requires-python bounds" in out

        def test_no_pyproject_toml(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
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

        def test_no_requires_python(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
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

        def test_python_version_file_used_when_no_requires_python(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Arrange
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / ".python-version").write_text("3.11\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should return the version from .python-version
            assert versions == [PythonVersion(major="3", minor="11")]

        def test_python_version_file_used_when_no_pyproject_toml(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Arrange
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / ".python-version").write_text("3.12\n")

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should return the version from .python-version
            assert versions == [PythonVersion(major="3", minor="12")]

        def test_python_version_file_used_in_bounds_warning(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange - .python-version says 3.10, but requires-python is >=3.11,<3.13
            monkeypatch.setattr(
                "usethis._backend.dispatch.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / ".python-version").write_text("3.10\n")
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
                PythonVersion(major="3", minor="11"),
                PythonVersion(major="3", minor="12"),
            ]
            # .python-version says 3.10, which is outside the range
            out, _err = capfd.readouterr()
            assert "Current Python version" in out
            assert "3.10" in out
            assert "outside requires-python bounds" in out

        def test_no_versions_match_uses_python_version_file(
            self,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange - requires-python constraint matches no known versions
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / ".python-version").write_text("3.11\n")
            (tmp_path / "pyproject.toml").write_text(
                """
[project]
requires-python = ">=3.20"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - empty match falls back to .python-version
            assert versions == [PythonVersion(major="3", minor="11")]

        def test_no_versions_match_falls_back_to_interpreter(
            self,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange - requires-python constraint matches no known versions, no
            # .python-version file present
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.none,
            )
            (tmp_path / "pyproject.toml").write_text(
                """
[project]
requires-python = ">=3.20"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - empty match falls back to interpreter
            current = PythonVersion.from_interpreter()
            assert versions == [current]

        def test_requires_python_error_in_warning_block_is_suppressed(
            self,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange - requires-python raises during the bounds-warning check (but not
            # during the main version enumeration); the exception must be silently
            # swallowed and the function must still return the resolved versions.
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
            # Patch get_requires_python as imported in the environ.python module so that
            # only the call in the bounds-warning block raises, not the call inside
            # get_required_minor_python_versions.
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_requires_python",
                lambda: (_ for _ in ()).throw(MissingRequiresPythonError("mocked")),
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert - should still return versions (warning block is a best-effort check)
            assert versions == [
                PythonVersion(major="3", minor="11"),
                PythonVersion(major="3", minor="12"),
            ]

    class TestUvBackend:
        def test_delegates_to_uv(
            self,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange
            expected = [PythonVersion(major="3", minor="11")]
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_backend",
                lambda: BackendEnum.uv,
            )
            monkeypatch.setattr(
                "usethis._integrations.environ.python.get_supported_uv_minor_python_versions",
                lambda: expected,
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                versions = get_supported_minor_python_versions()

            # Assert
            assert versions == expected
