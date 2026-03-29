from pathlib import Path

import pytest

import usethis._backend.uv.call
from usethis._backend.uv.errors import UVInitError, UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.errors import PyprojectTOMLInitError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._init import (
    _BUILD_SYSTEM_CONFIG,
    ensure_pyproject_toml,
    project_init,
    write_simple_requirements_txt,
)
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum
from usethis._types.build_backend import BuildBackendEnum


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
        def mock_call_uv_subprocess(*_: object, **__: object) -> None:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.call,
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

    def test_build_backend_uv_for_uv_backend(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager() as manager,
            usethis_config.set(build_backend=BuildBackendEnum.uv),
        ):
            # Act
            project_init()

            # Assert
            assert manager[["build-system", "build-backend"]] == "uv_build"

    def test_poetry_backend(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        calls: list[str] = []

        def mock_opinionated_poetry_init() -> None:
            calls.append("init")
            (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        monkeypatch.setattr(
            "usethis._init.opinionated_poetry_init",
            mock_opinionated_poetry_init,
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.poetry),
        ):
            project_init()

        assert len(calls) == 1
        assert (tmp_path / "pyproject.toml").exists()


class TestBuildSystemConfig:
    def test_keys_match_enum(self):
        assert set(_BUILD_SYSTEM_CONFIG.keys()) == set(BuildBackendEnum)


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
        def mock_call_uv_subprocess(*_: object, **__: object) -> None:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.call,
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

    def test_poetry_backend(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        calls: list[str] = []

        def mock_ensure_pyproject_toml_via_poetry(*, author: bool = True) -> None:
            _ = author
            calls.append("ensure")
            (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        monkeypatch.setattr(
            "usethis._init.ensure_pyproject_toml_via_poetry",
            mock_ensure_pyproject_toml_via_poetry,
        )

        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            usethis_config.set(backend=BackendEnum.poetry),
        ):
            ensure_pyproject_toml()

        assert len(calls) == 1
        assert (tmp_path / "pyproject.toml").exists()


class TestWriteSimpleRequirementsTxt:
    def test_no_pyproject_toml(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            write_simple_requirements_txt()

        # Assert
        assert (tmp_path / "requirements.txt").exists()
        content = (tmp_path / "requirements.txt").read_text()
        assert content == "-e .\n"

    def test_no_dependencies(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = []
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            write_simple_requirements_txt()

        # Assert
        assert (tmp_path / "requirements.txt").exists()
        content = (tmp_path / "requirements.txt").read_text()
        assert content == "-e .\n"

    def test_with_dependencies(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = [
    "requests",
    "click>=8.0",
]
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            write_simple_requirements_txt()

        # Assert
        assert (tmp_path / "requirements.txt").exists()
        content = (tmp_path / "requirements.txt").read_text()
        assert content == "-e .\nrequests\nclick\n"

    def test_with_dependencies_with_extras(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = [
    "requests[security]",
    "click[extra1,extra2]>=8.0",
]
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            write_simple_requirements_txt()

        # Assert
        assert (tmp_path / "requirements.txt").exists()
        content = (tmp_path / "requirements.txt").read_text()
        # Note: extras should be preserved (sorted alphabetically per frozenset behavior)
        assert content == "-e .\nrequests[security]\nclick[extra1,extra2]\n"

    def test_overwrites_existing_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "requirements.txt").write_text("old content")

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            write_simple_requirements_txt()

        # Assert
        content = (tmp_path / "requirements.txt").read_text()
        assert content == "-e .\n"
        assert "old content" not in content
