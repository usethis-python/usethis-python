from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestREADME:
    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["readme", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "README.md").exists()
        assert result.output == (
            "✔ Writing 'README.md'.\n"
            "☐ Populate 'README.md' to help users understand the project.\n"
        )
