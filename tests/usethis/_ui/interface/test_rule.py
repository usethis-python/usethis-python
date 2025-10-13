from pathlib import Path

from usethis._config_file import files_manager
from usethis._core.rule import ignore_rules
from usethis._core.tool import use_deptry
from usethis._subprocess import call_subprocess
from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestRule:
    def test_add(self, tmp_path: Path):
        # Arrange
        (tmp_path / "ruff.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "RUF001"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == """✔ Selecting Ruff rule 'RUF001' in 'ruff.toml'.\n"""

    def test_deselect(self, tmp_path: Path):
        # Arrange
        (tmp_path / "ruff.toml").write_text(
            """\
[lint]
select = ["RUF001"]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "RUF001", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == """✔ Deselecting Ruff rule 'RUF001' in 'ruff.toml'.\n"""

    def test_ignore(self, tmp_path: Path):
        # Arrange
        (tmp_path / "ruff.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "RUF001", "--ignore"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == """✔ Ignoring Ruff rule 'RUF001' in 'ruff.toml'.\n"""

    def test_unignore(self, tmp_path: Path):
        # Arrange
        (tmp_path / "ruff.toml").write_text(
            """\
[lint]
ignore = ["RUF001"]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "RUF001", "--remove", "--ignore"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == """✔ No longer ignoring Ruff rule 'RUF001' in 'ruff.toml'.\n"""
        )

    def test_runs_after_ignore(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            # Arrange
            use_deptry()

            # Act
            ignore_rules(rules=["DEP001"])

            # Assert (that deptry runs without error)
            call_subprocess(["deptry", "."])

    def test_none_backend_no_pyproject_toml(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "FAKE", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "pyproject.toml").exists()
        assert result.output.replace("\n", "") == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Writing 'ruff.toml'.\n"
            "✔ Adding Ruff config to 'ruff.toml'.\n"
            "✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'ruff.toml'.\n"
            "✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'ruff.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "✔ Selecting Ruff rule 'FAKE' in 'ruff.toml'.\n"
        ).replace("\n", "")

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["rule", "FAKE", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output.replace("\n", "") == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Adding Ruff config to 'pyproject.toml'.\n"
            "✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
            "✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "✔ Selecting Ruff rule 'FAKE' in 'pyproject.toml'.\n"
        ).replace("\n", "")
