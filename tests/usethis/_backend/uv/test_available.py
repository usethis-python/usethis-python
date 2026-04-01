from pathlib import Path

import pytest

import usethis._backend.uv.available
from usethis._backend.uv.available import _is_uv_a_dep, is_uv_available
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config_file import files_manager
from usethis._test import change_cwd


class TestIsUVAvailable:
    def test_available_when_running_test_suite(self):
        # Having uv is a pre-requisite for running the test suite
        assert is_uv_available()

    def test_mock_not_available(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange

        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.available,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_uv_available()

        # Assert
        assert not result

    def test_fallback_to_project_dep(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
dependencies = ["uv>=0.1.0"]
""")

        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.available,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_uv_available()

        # Assert
        assert result

    def test_fallback_to_dep_group(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
dev = ["uv>=0.1.0"]
""")

        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.available,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_uv_available()

        # Assert
        assert result

    def test_not_available_when_other_dep(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
dependencies = ["requests>=2.0"]
""")

        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.available,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = is_uv_available()

        # Assert
        assert not result


class TestIsUvADep:
    def test_no_pyproject(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            assert not _is_uv_a_dep()

    def test_uv_in_project_deps(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
dependencies = ["uv>=0.1.0"]
""")

        # Act, Assert
        with change_cwd(tmp_path), files_manager():
            assert _is_uv_a_dep()

    def test_uv_in_dep_group(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
dev = ["uv>=0.1.0"]
""")

        # Act, Assert
        with change_cwd(tmp_path), files_manager():
            assert _is_uv_a_dep()

    def test_no_uv_dep(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
dependencies = ["requests>=2.0"]
""")

        # Act, Assert
        with change_cwd(tmp_path), files_manager():
            assert not _is_uv_a_dep()

    def test_empty_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        # Act, Assert
        with change_cwd(tmp_path), files_manager():
            assert not _is_uv_a_dep()
