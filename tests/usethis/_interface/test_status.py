from pathlib import Path

from typer.testing import CliRunner

from usethis._app import app
from usethis._test import change_cwd


class TestStatus:
    def test_successful(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["status", "beta"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "✔ Writing 'pyproject.toml'.\n✔ Setting development status to '4 - Beta'.\n"
        )
