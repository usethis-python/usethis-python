from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestStatus:
    def test_successful(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["status", "beta"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "✔ Writing 'pyproject.toml'.\n✔ Setting the development status to '4 - Beta'.\n"
        )

    def test_numerical_code(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["status", "5"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "✔ Writing 'pyproject.toml'.\n✔ Setting the development status to '5 - Production/Stable'.\n"
        )

    def test_no_args(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["status"])

        # Assert
        assert result.exit_code == 2, result.output

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["status", "beta", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "✔ Writing 'pyproject.toml'.\n"
            "✔ Setting the development status to '4 - Beta'.\n"
        )
