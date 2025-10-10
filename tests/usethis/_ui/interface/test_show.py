from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.show import app


class TestName:
    def test_output(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "fun"
        path.mkdir()

        # Act
        runner = CliRunner()
        with change_cwd(path):
            result = runner.invoke_safe(app, ["name"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == """fun\n"""

    def test_invalid_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["name"])

        # Assert
        assert result.exit_code == 1, result.output


class TestSonarqube:
    def test_runs(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.usethis.sonarqube]
project-key = "fun"

[tool.coverage.xml.output]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output

    def test_missing_key(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 1, result.output

    def test_invalid_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 1, result.output
