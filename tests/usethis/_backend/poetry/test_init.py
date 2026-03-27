from pathlib import Path

import pytest

import usethis._backend.poetry.init
from usethis._backend.poetry.errors import PoetryInitError, PoetrySubprocessFailedError
from usethis._backend.poetry.init import (
    ensure_pyproject_toml_via_poetry,
    opinionated_poetry_init,
)
from usethis._config import usethis_config
from usethis._file.pyproject_toml.errors import PyprojectTOMLInitError
from usethis._types.backend import BackendEnum


class TestEnsurePyprojectTomlViaPoetry:
    def test_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        captured_args: list[str] = []

        def mock_call_poetry_subprocess(
            args: list[str], *, change_toml: bool
        ) -> str:
            _ = change_toml
            captured_args.extend(args)
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.init,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, project_dir=tmp_path
        ):
            ensure_pyproject_toml_via_poetry()

        assert captured_args == ["init", "--name", tmp_path.name]

    def test_failure_raises_init_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        def mock_call_poetry_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise PoetrySubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.init,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        with (
            usethis_config.set(
                backend=BackendEnum.poetry, project_dir=tmp_path
            ),
            pytest.raises(PyprojectTOMLInitError),
        ):
            ensure_pyproject_toml_via_poetry()

    def test_author_param_accepted(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        """The author parameter is accepted for API compatibility but ignored."""

        def mock_call_poetry_subprocess(*_: object, **__: object) -> str:
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.init,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, project_dir=tmp_path
        ):
            # Should not raise, regardless of author value
            ensure_pyproject_toml_via_poetry(author=False)


class TestOpinionatedPoetryInit:
    def test_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        captured_args: list[str] = []

        def mock_call_poetry_subprocess(
            args: list[str], *, change_toml: bool
        ) -> str:
            _ = change_toml
            captured_args.extend(args)
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.init,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, project_dir=tmp_path
        ):
            opinionated_poetry_init()

        assert captured_args == ["init", "--name", tmp_path.name]

    def test_failure_raises_poetry_init_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        def mock_call_poetry_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise PoetrySubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.init,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        with (
            usethis_config.set(
                backend=BackendEnum.poetry, project_dir=tmp_path
            ),
            pytest.raises(PoetryInitError),
        ):
            opinionated_poetry_init()
