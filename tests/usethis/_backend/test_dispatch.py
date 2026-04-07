from pathlib import Path

import pytest

import usethis._backend.poetry.call
import usethis._backend.uv.available
from _test import change_cwd
from usethis._backend.dispatch import call_backend_subprocess, get_backend
from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._types.backend import BackendEnum
from usethis.errors import BackendSubprocessFailedError


class TestGetBackend:
    def test_non_auto_remains(self):
        for backend in BackendEnum:
            if backend is not BackendEnum.auto:
                with usethis_config.set(backend=backend):
                    assert get_backend() == backend

    def test_uv_used(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.lock").touch()

        # Act
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.auto):
            result = get_backend()

        # Assert
        assert result == BackendEnum.uv

    def test_uv_not_used_but_available(self, tmp_path: Path):
        # Act
        with (
            change_cwd(tmp_path),
            usethis_config.set(backend=BackendEnum.auto),
            files_manager(),
        ):
            result = get_backend()

        # Assert
        assert result == BackendEnum.uv

    def test_uv_not_used_and_not_available(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange

        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.available,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with (
            change_cwd(tmp_path),
            usethis_config.set(backend=BackendEnum.auto),
            files_manager(),
        ):
            result = get_backend()

        # Assert
        assert result == BackendEnum.none

    def test_poetry_used(self, tmp_path: Path):
        # Arrange
        (tmp_path / "poetry.lock").touch()

        # Act
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.auto):
            result = get_backend()

        # Assert
        assert result == BackendEnum.poetry

    def test_pyproject_already_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with (
            change_cwd(tmp_path),
            usethis_config.set(backend=BackendEnum.auto),
            files_manager(),
        ):
            result = get_backend()

        # Assert
        assert result == BackendEnum.none


class TestCallBackendSubprocess:
    def test_dispatches_to_uv(self, tmp_path: Path):
        with usethis_config.set(backend=BackendEnum.uv, project_dir=tmp_path):
            result = call_backend_subprocess(
                ["help"], change_toml=False, backend=BackendEnum.uv
            )
        assert isinstance(result, str)

    def test_dispatches_to_poetry(self, tmp_path: Path):
        with usethis_config.set(backend=BackendEnum.poetry, project_dir=tmp_path):
            result = call_backend_subprocess(
                ["--version"], change_toml=False, backend=BackendEnum.poetry
            )
        assert "Poetry" in result

    def test_none_backend_raises_value_error(self):
        with pytest.raises(ValueError, match="no backend is active"):
            call_backend_subprocess(
                ["help"], change_toml=False, backend=BackendEnum.none
            )

    def test_uv_failure_is_backend_error(self, tmp_path: Path):
        with (
            usethis_config.set(backend=BackendEnum.uv, project_dir=tmp_path),
            pytest.raises(BackendSubprocessFailedError),
        ):
            call_backend_subprocess(
                ["does-not-exist"], change_toml=False, backend=BackendEnum.uv
            )

    def test_poetry_failure_is_backend_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def mock_call_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise PoetrySubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_poetry_subprocess",
            mock_call_subprocess,
        )

        with (
            usethis_config.set(backend=BackendEnum.poetry, project_dir=tmp_path),
            pytest.raises(BackendSubprocessFailedError),
        ):
            call_backend_subprocess(
                ["run", "some-cmd"], change_toml=False, backend=BackendEnum.poetry
            )
