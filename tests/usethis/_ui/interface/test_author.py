from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestAuthor:
    def test_add_name(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["author", "--name", "John Doe"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_add_name_email(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["author", "--name", "John Doe", "--email", "jdoe@example.com"]
            )

        # Assert
        assert result.exit_code == 0, result.output

    def test_missing_name(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["author"])

        # Assert
        assert result.exit_code == 2, result.output

    def test_error(self, tmp_path: Path):
        # Arrange
        # Syntax error in pyproject.toml to trigger an error
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["author", "--name", ""])

        # Assert
        assert result.exit_code == 1, result.output

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["author", "--backend", "none", "--name", "John Doe"]
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            """\
✔ Writing 'pyproject.toml'.
✔ Setting 'John Doe' as an author.
"""
        )
