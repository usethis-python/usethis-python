from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestDocstyle:
    def test_google_runs(self, tmp_path: Path):
        with change_cwd(tmp_path):
            runner = CliRunner()
            runner.invoke_safe(app, ["docstyle", "google"])

    def test_invalid_pyproject_toml(self, tmp_path: Path):
        # Arrange
        invalid_pyproject_toml = tmp_path / "pyproject.toml"
        invalid_pyproject_toml.write_text("[")

        # Act
        with change_cwd(tmp_path):
            runner = CliRunner()
            with change_cwd(tmp_path):
                result = runner.invoke_safe(app, ["docstyle", "google"])

        # Assert
        assert result.exit_code == 1, result.output

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pyproject_toml_success(self, tmp_path: Path):
        # https://github.com/usethis-python/usethis-python/issues/507

        # Arrange
        valid_pyproject_toml = tmp_path / "pyproject.toml"
        valid_pyproject_toml.touch()

        # Act
        with change_cwd(tmp_path):
            runner = CliRunner()
            if not usethis_config.offline:
                result = runner.invoke_safe(app, ["docstyle", "numpy"])
            else:
                result = runner.invoke_safe(app, ["docstyle", "numpy", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            "✔ Setting docstring style to 'numpy' in 'pyproject.toml'." in result.output
        )

        assert valid_pyproject_toml.exists()
        content = valid_pyproject_toml.read_text()
        assert (
            """\
[tool.ruff]
line-length = 88
format.docstring-code-format = true
lint.pydocstyle.convention = "numpy"\
"""
            in content
        )

    def test_adding_to_existing_file(self, tmp_path: Path):
        # Arrange
        existing_pyproject_toml = tmp_path / "pyproject.toml"
        existing_pyproject_toml.write_text(
            """\
[project]
name = "usethis"
version = "0.1.0"

[tool.ruff]
lint.select = [ "A" ]
"""
        )

        # Act
        with change_cwd(tmp_path):
            runner = CliRunner()
            result = runner.invoke_safe(app, ["docstyle", "pep257"])

        # Assert
        assert result.exit_code == 0, result.output
        content = existing_pyproject_toml.read_text()
        assert "[lint.pydocstyle]" not in content  # Wrong section name

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_default(self, tmp_path: Path):
        # Arrange
        default_pyproject_toml = tmp_path / "pyproject.toml"
        default_pyproject_toml.touch()

        # Act
        with change_cwd(tmp_path):
            runner = CliRunner()
            if not usethis_config.offline:
                result = runner.invoke_safe(app, ["docstyle"])
            else:
                result = runner.invoke_safe(app, ["docstyle", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            "✔ Setting docstring style to 'google' in 'pyproject.toml'."
            in result.output
        )

        content = default_pyproject_toml.read_text()
        assert "google" in content

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["docstyle", "numpy", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Adding Ruff config to 'pyproject.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "✔ Setting docstring style to 'numpy' in 'pyproject.toml'.\n"
            "✔ Selecting Ruff rules 'D2', 'D3', 'D4' in 'pyproject.toml'.\n"
        )

    def test_none_backend_no_pyproject_toml(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["docstyle", "numpy", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Writing 'ruff.toml'.\n"
            "✔ Adding Ruff config to 'ruff.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "✔ Setting docstring style to 'numpy' in 'ruff.toml'.\n"
            "✔ Selecting Ruff rules 'D2', 'D3', 'D4' in 'ruff.toml'.\n"
        )
