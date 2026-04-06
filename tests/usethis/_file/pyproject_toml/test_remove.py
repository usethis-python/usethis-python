from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._file.pyproject_toml.remove import remove_pyproject_toml
from usethis._test import change_cwd


class TestRemovePyprojectTOML:
    def test_removed(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.touch()

        # Act
        with change_cwd(tmp_path), files_manager():
            remove_pyproject_toml()

        # Assert
        assert not pyproject_path.exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Removing 'pyproject.toml' file\n"
