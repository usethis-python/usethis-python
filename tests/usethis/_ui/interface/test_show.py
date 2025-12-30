from pathlib import Path

from usethis._config import usethis_config
from usethis._test import CliRunner, change_cwd
from usethis._types.backend import BackendEnum
from usethis._ui.interface.show import app


class TestBackend:
    def test_uv_backend(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.lock").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["backend"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "uv\n"

    def test_none_backend(self, tmp_path: Path):
        # Arrange

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
            result = runner.invoke_safe(app, ["backend"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "none\n"


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
