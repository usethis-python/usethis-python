from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.browse import app


class TestBrowse:
    def test_success(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["usethis"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_missing_package_name(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, [])

        # Assert
        assert result.exit_code == 2, result.output
