import re
from pathlib import Path

import pytest

from usethis._integrations.pyproject.core import (
    PyProjectTOMLValueAlreadySetError,
    PyProjectTOMLValueMissingError,
    append_config_list,
    get_config_value,
    remove_config_value,
    set_config_value,
)
from usethis._integrations.pyproject.io_ import PyProjectTOMLNotFoundError
from usethis._test import change_cwd


class TestGetConfigValue:
    def test_pyproject_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            get_config_value(["tool", "usethis", "key"])

    def test_key_does_not_exist(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = "value"
"""
        )

        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(KeyError):
            get_config_value(["tool", "usethis", "key2"])

    def test_single_key(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = "value"
"""
        )

        # Act
        with change_cwd(tmp_path):
            value = get_config_value(["tool", "usethis", "key"])

        # Assert
        assert value == "value"


class TestSetConfigValue:
    def test_empty(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path):
            set_config_value(["tool", "usethis", "key"], "value")

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key = "value"
"""
        )

    def test_update_exists_ok(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = "value1"
"""
        )

        # Act
        with change_cwd(tmp_path):
            set_config_value(["tool", "usethis", "key"], "value2", exists_ok=True)

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key = "value2"
"""
        )

    def test_update_not_exists_ok(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = "value1"
"""
        )

        # Act
        with (
            change_cwd(tmp_path),
            pytest.raises(
                PyProjectTOMLValueAlreadySetError,
                match=re.escape(
                    "Configuration value 'tool.usethis.key' is already set."
                ),
            ),
        ):
            set_config_value(["tool", "usethis", "key"], "value2", exists_ok=False)

    def test_update_mixed_nested(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key1 = "value1"
key2 = "value2"
"""
        )

        # Act
        with change_cwd(tmp_path):
            set_config_value(["tool", "usethis", "key1"], "value3", exists_ok=True)

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key1 = "value3"
key2 = "value2"
"""
        )


class TestRemoveConfigValue:
    def test_already_missing(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act, Assert
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLValueMissingError):
            remove_config_value(["tool", "usethis", "key"])

    def test_missing_pyproject(self, tmp_path: Path):
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            remove_config_value(["tool", "usethis", "key"])

    def test_single_key(self, tmp_path: Path):
        """This checks the empty section cleanup."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = "value"
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_config_value(["tool", "usethis", "key"])

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == ""

    def test_multi_key(self, tmp_path: Path):
        """This checks the empty section cleanup."""
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key1 = "value1"
key2 = "value2"
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_config_value(["tool", "usethis", "key1"])

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key2 = "value2"
"""
        )

    def test_already_missing_okay(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path):
            remove_config_value(["tool", "usethis", "key"], missing_ok=True)

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == ""


class TestAppendConfigList:
    def test_empty(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path):
            append_config_list(["tool", "usethis", "key"], ["value"])

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key = ["value"]
"""
        )

    def test_add_one(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[tool.usethis]
key = ["value1"]
"""
        )

        # Act
        with change_cwd(tmp_path):
            append_config_list(["tool", "usethis", "key"], ["value2"])

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[tool.usethis]
key = ["value1", "value2"]
"""
        )
