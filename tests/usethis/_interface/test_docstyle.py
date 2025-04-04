from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from usethis._app import app
from usethis._interface.docstyle import docstyle
from usethis._test import change_cwd


class TestDocstyle:
    def test_invalid_style(self, capfd: pytest.CaptureFixture[str]):
        with pytest.raises(typer.Exit):
            docstyle("invalid_style")
        out, err = capfd.readouterr()
        assert "Invalid docstring style" in out
        assert not err

    def test_google_runs(self, tmp_path: Path):
        with change_cwd(tmp_path):
            docstyle("google")

    def test_invalid_pyproject_toml(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        invalid_pyproject_toml = tmp_path / "pyproject.toml"
        invalid_pyproject_toml.write_text("[")

        # Act
        with change_cwd(tmp_path):
            runner = CliRunner()
            with change_cwd(tmp_path):
                result = runner.invoke(app, ["docstyle", "google"])

        # Assert
        assert result.exit_code == 1, result.output
