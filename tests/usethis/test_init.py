from pathlib import Path
from typing import Any

import pytest

import usethis._integrations.backend.uv.call
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._init import ensure_pyproject_toml, project_init
from usethis._integrations.backend.uv.errors import UVInitError, UVSubprocessFailedError
from usethis._integrations.file.pyproject_toml.errors import PyprojectTOMLInitError
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum


class TestProjectInit:
    def test_empty_dir(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            project_init()

        # Assert
        assert (tmp_path / "pyproject.toml").exists()

    def test_short_circuits_if_pyproject_toml_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("test")

        # Act (& Assert there is no error)
        with change_cwd(tmp_path):
            project_init()

    def test_subprocess_failed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_call_uv_subprocess(*_: Any, **__: Any) -> None:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._integrations.backend.uv.call,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager(), pytest.raises(UVInitError):
            project_init()

    def test_none_backend(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        path = tmp_path / "myproj"
        path.mkdir()

        with usethis_config.set(backend=BackendEnum.none):
            # Act
            with change_cwd(path), files_manager():
                project_init()

            # Assert
            assert (path / "pyproject.toml").exists()
            assert (path / "README.md").exists()
            assert (path / "src").exists()
            assert (path / "src").is_dir()
            assert (path / "src" / "myproj").exists()
            assert (path / "src" / "myproj").is_dir()
            assert (path / "src" / "myproj" / "__init__.py").exists()
            assert (path / "src" / "myproj" / "py.typed").exists()
            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Writing 'pyproject.toml' and initializing project.\n"

    def test_build_backend_is_hatch_for_none_backend(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager() as manager,
            usethis_config.set(backend=BackendEnum.none),
        ):
            # Act
            project_init()

            # Assert
            assert manager[["build-system", "build-backend"]] == "hatchling.build"


class TestEnsurePyprojectTOML:
    def test_created(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "pyproject.toml").exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Writing 'pyproject.toml'.\n"

    def test_already_exists_unchanged(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("test")

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == "test"
        out, err = capfd.readouterr()
        assert not err
        assert not out

    def test_hello_py_respected(self, tmp_path: Path):
        # Arrange
        (tmp_path / "hello.py").write_text("test")

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "hello.py").exists()
        assert (tmp_path / "hello.py").read_text() == "test"

    def test_main_py_respected(self, tmp_path: Path):
        # Arrange
        (tmp_path / "main.py").write_text("test")

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert (tmp_path / "main.py").exists()
        assert (tmp_path / "main.py").read_text() == "test"

    def test_no_hello_py_created(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / "hello.py").exists()

    def test_no_main_py_created(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / "main.py").exists()

    def test_no_readme(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / "README.md").exists()

    def test_no_pin_python(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / ".python-version").exists()

    def test_no_vcs(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            ensure_pyproject_toml()

        # Assert
        assert not (tmp_path / ".git").exists()

    def test_subprocess_failed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_call_uv_subprocess(*_: Any, **__: Any) -> None:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._integrations.backend.uv.call,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(PyprojectTOMLInitError),
        ):
            ensure_pyproject_toml()

    def test_build_backend(self, tmp_path: Path):
        with change_cwd(tmp_path), PyprojectTOMLManager():
            # Act
            ensure_pyproject_toml()

            # Assert
            assert ["build-system"] in PyprojectTOMLManager()
