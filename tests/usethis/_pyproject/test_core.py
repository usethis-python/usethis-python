from pathlib import Path

from usethis._pyproject.core import append_config_list
from usethis._test import change_cwd


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
