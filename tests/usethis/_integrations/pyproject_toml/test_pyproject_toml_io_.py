from pathlib import Path

import pytest
from tomlkit import TOMLDocument

from usethis._integrations.pyproject_toml.errors import (
    PyprojectTOMLDecodeError,
    PyprojectTOMLNotFoundError,
)
from usethis._integrations.pyproject_toml.io_ import (
    PyprojectTOMLManager,
    UnexpectedPyprojectTOMLIOError,
    UnexpectedPyprojectTOMLOpenError,
)
from usethis._test import change_cwd


class TestPyprojectTOMLManager:
    def test_context_manager_locking(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager = PyprojectTOMLManager()

        # Act & Assert
        assert not manager.is_locked()
        with manager:
            assert manager.is_locked()
        assert not manager.is_locked()

    def test_unexpected_open_error(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager1 = PyprojectTOMLManager()
            manager2 = PyprojectTOMLManager()

        # Act & Assert
        with manager1, pytest.raises(UnexpectedPyprojectTOMLOpenError), manager2:
            pass

    def test_get_without_opening(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager = PyprojectTOMLManager()

        # Act & Assert
        with pytest.raises(UnexpectedPyprojectTOMLIOError):
            manager.get()

    def test_commit_without_opening(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager = PyprojectTOMLManager()

        # Act & Assert
        with pytest.raises(UnexpectedPyprojectTOMLIOError):
            manager.commit(TOMLDocument())

    def test_read_file_not_found(self, tmp_path: Path):
        with change_cwd(tmp_path):
            # Arrange
            manager = PyprojectTOMLManager()

            # Act & Assert
            with pytest.raises(PyprojectTOMLNotFoundError), manager:
                manager.read_file()

    def test_read_file_invalid_toml(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            (tmp_path / "pyproject.toml").write_text("invalid_toml")

            manager = PyprojectTOMLManager()

        # Act & Assert
        with pytest.raises(PyprojectTOMLDecodeError), manager:
            manager.read_file()

    def test_commit_and_get(self, tmp_path: Path):
        with change_cwd(tmp_path):
            # Arrange
            manager = PyprojectTOMLManager()
            toml_data = TOMLDocument()
            toml_data["tool"] = {"test": "value"}

            # Act
            with manager:
                manager.commit(toml_data)
                result = manager.get()

        # Assert
        assert result == toml_data

    def test_write_file(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager = PyprojectTOMLManager()
            toml_data = TOMLDocument()
            toml_data["tool"] = {"test": "value"}

        # Act
        with manager:
            manager.commit(toml_data)
            manager.write_file()

    def test_double_read_fails(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            (tmp_path / "pyproject.toml").write_text("tool = { test = 'value' }")
            manager = PyprojectTOMLManager()

        # Act & Assert
        with manager:
            manager.read_file()
            with pytest.raises(UnexpectedPyprojectTOMLIOError):
                manager.read_file()

    def test_exit_without_lock(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            manager = PyprojectTOMLManager()
        manager.unlock()

        # Act & Assert
        manager.__exit__(None, None, None)  # Should not raise an error

    def test_get_entails_read(self, tmp_path: Path):
        # Arrange
        with change_cwd(tmp_path):
            (tmp_path / "pyproject.toml").write_text("tool = { test = 'value' }")
            manager = PyprojectTOMLManager()

        # Act
        with manager:
            result = manager.get()

        # Assert
        assert result.value["tool"]["test"] == "value"
