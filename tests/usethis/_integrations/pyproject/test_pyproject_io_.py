from pathlib import Path

import pytest
from tomlkit import TOMLDocument

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLDecodeError,
    PyProjectTOMLNotFoundError,
)
from usethis._integrations.pyproject.io_ import (
    PyprojectTOMLIOManager,
    PyprojectTOMLOpener,
    UnexpectedPyprojectTOMLOpenError,
    pyproject_toml_io_manager,
    read_pyproject_toml,
    write_pyproject_toml,
)
from usethis._test import change_cwd


class TestPyprojectTOMLOpener:
    class TestInit:
        def test_path(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "pyproject.toml"

            # Act
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Assert
            assert opener.path == path

        def test_content_starts_empty(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Assert
            assert opener.content == {}

        def test_open_starts_false(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Assert
            assert not opener.open

        def test_set_starts_false(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Assert
            assert not opener._set

    class TestRead:
        def test_not_set(self, tmp_path: Path):
            # Arrange
            opener = PyprojectTOMLOpener()

            # Act, Assert
            with pytest.raises(UnexpectedPyprojectTOMLOpenError):
                opener.read()

        def test_not_open(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()
            opener._set = True
            opener.open = False
            path = tmp_path / "pyproject.toml"
            path.write_text('name = "usethis"')

            # Act
            result = opener.read()

            # Assert
            assert opener.open
            assert result == {
                "name": "usethis",
            }

        def test_open(self):
            # Arrange
            opener = PyprojectTOMLOpener()
            opener._set = True
            opener.open = True

            # Act
            result = opener.read()

            # Assert
            assert result == opener.content

    class TestWrite:
        def test_not_set(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Act, Assert
            with pytest.raises(UnexpectedPyprojectTOMLOpenError):
                opener.write(TOMLDocument())

        def test_content(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()
            opener._set = True
            toml_document = TOMLDocument()
            toml_document["name"] = "usethis"

            # Act
            opener.write(toml_document)

            # Assert
            assert opener.content == toml_document

    class TestWriteFile:
        def test_output(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            opener.open = True
            opener._set = True
            toml_document = TOMLDocument()
            toml_document["name"] = "usethis"
            opener.write(toml_document)

            # Act
            opener.write_file()

            # Assert
            assert (
                (tmp_path / "pyproject.toml").read_text()
                == """\
name = "usethis"
"""
            )

    class TestEnterExit:
        def test_set(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            # Act, Assert
            assert not opener._set
            with opener:
                assert opener._set
            assert not opener._set

        def test_write_on_exit(self, tmp_path: Path):
            # Arrange
            with change_cwd(tmp_path):
                opener = PyprojectTOMLOpener()

            opener.open = True
            opener._set = True
            toml_document = TOMLDocument()
            toml_document["name"] = "usethis"
            opener.write(toml_document)

            # Act
            with opener:
                pass

            # Assert
            assert (
                (tmp_path / "pyproject.toml").read_text()
                == """\
name = "usethis"
"""
            )


class TestReadPyprojectTOML:
    def test_empty(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.touch()

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            result = read_pyproject_toml().value

        # Assert
        assert result == {}

    def test_single_map(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.write_text('name = "usethis"')

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            result = read_pyproject_toml().value

        # Assert
        assert result == {"name": "usethis"}

    def test_invalid_toml(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.write_text("name =")

        # Act, Assert
        with (
            change_cwd(tmp_path),
            pyproject_toml_io_manager.open(),
            pytest.raises(PyProjectTOMLDecodeError),
        ):
            read_pyproject_toml().value

    def test_missing(self, tmp_path: Path):
        # Act, Assert
        with (
            change_cwd(tmp_path),
            pyproject_toml_io_manager.open(),
            pytest.raises(PyProjectTOMLNotFoundError),
        ):
            read_pyproject_toml().value


class TestWritePyprojectTOML:
    def test_content(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "pyproject.toml"
        path.touch()
        toml_document = TOMLDocument()
        toml_document["name"] = "usethis"

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            write_pyproject_toml(toml_document)

        # Assert
        assert (
            path.read_text()
            == """\
name = "usethis"
"""
        )


class TestPyprojectTOMLIOManager:
    class TestInit:
        def test_opener(self):
            # Act
            result = PyprojectTOMLIOManager()

            # Assert
            assert isinstance(result._opener, PyprojectTOMLOpener)

        def test_set(self):
            # Act
            result = PyprojectTOMLIOManager()

            # Assert
            assert not result._set

    class TestOpener:
        def test_opener_starts_unset(self):
            # Arrange
            manager = PyprojectTOMLIOManager()
            manager._opener._set = False

            # Act, Assert
            with pytest.raises(UnexpectedPyprojectTOMLOpenError):
                manager.opener

        def test_set_opener_starts_set(self):
            # Arrange
            manager = PyprojectTOMLIOManager()
            manager._opener._set = True
            manager._set = True

            # Act
            opener = manager.opener

            # Assert
            assert manager._set
            assert opener is manager._opener

        def test_unset_opener_starts_set(self):
            # Arrange
            manager = PyprojectTOMLIOManager()
            manager._opener._set = True
            manager._set = False

            # Act, Assert
            with pytest.raises(UnexpectedPyprojectTOMLOpenError):
                manager.opener

    class TestOpen:
        def test_change_from_init(self):
            # Arrange
            manager = PyprojectTOMLIOManager()
            opener = manager._opener

            # Act
            result = manager.open()

            # Assert
            assert result is not opener
            assert isinstance(result, PyprojectTOMLOpener)
