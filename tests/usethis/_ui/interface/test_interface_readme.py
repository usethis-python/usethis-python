from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestReadme:
    def test_runs(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["readme"])

        # Assert
        assert result.exit_code == 0, result.output
        # Check no badges have been added
        assert "ruff" not in (tmp_path / "README.md").read_text()
        assert "pre-commit" not in (tmp_path / "README.md").read_text()

    def test_badges(self, tmp_path: Path):
        # Arrange
        (tmp_path / "ruff.toml").touch()
        (tmp_path / ".pre-commit-config.yaml").touch()
        (tmp_path / "uv.lock").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["readme", "--badges"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "README.md").exists()
        # and check the badges get created
        assert "ruff" in (tmp_path / "README.md").read_text()
        assert "pre-commit" in (tmp_path / "README.md").read_text()
        assert "uv" in (tmp_path / "README.md").read_text()

    def test_invalid_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["readme", "--badges"])

        # Assert
        assert result.exit_code == 1, result.output
