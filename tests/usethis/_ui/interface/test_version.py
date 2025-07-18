from pathlib import Path

from typer.testing import CliRunner

from usethis._test import change_cwd
from usethis._ui.app import app


class TestVersion:
    def test_runs(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["version"])

        # Assert
        assert result.exit_code == 0, result.output
