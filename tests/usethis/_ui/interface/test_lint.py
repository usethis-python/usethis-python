from pathlib import Path

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestLint:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["lint"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="ruff") in get_deps_from_group("dev")
            assert Dependency(name="deptry") in get_deps_from_group("dev")

        # Check Ruff formatter is not added
        txt = (tmp_path / "pyproject.toml").read_text()
        assert "format" not in txt
        assert "lint" in txt

    def test_none_backend_no_pyproject_toml(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["lint", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()  # from deptry config
        assert result.output.replace("\n", "") == (
            "☐ Add the dev dependency 'deptry'.\n"
            "✔ Writing 'pyproject.toml'.\n"
            "✔ Adding deptry config to 'pyproject.toml'.\n"
            "☐ Run 'deptry .' to run deptry.\n"
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Adding Ruff config to 'pyproject.toml'.\n"
            "✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
            "✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
        ).replace("\n", "")

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["lint", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output.replace("\n", "") == (
            "☐ Add the dev dependency 'deptry'.\n"
            "✔ Adding deptry config to 'pyproject.toml'.\n"
            "☐ Run 'deptry .' to run deptry.\n"
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Adding Ruff config to 'pyproject.toml'.\n"
            "✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
            "✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
        ).replace("\n", "")
