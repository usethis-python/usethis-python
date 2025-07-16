from pathlib import Path

from typer.testing import CliRunner

from usethis._test import change_cwd
from usethis._ui.app import app


class TestList:
    def test_success(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["list"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_error(self, tmp_path: Path):
        # Arrange
        # Syntax error in pyproject.toml to trigger an error
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["list"])

        # Assert
        assert result.exit_code == 1, result.output
