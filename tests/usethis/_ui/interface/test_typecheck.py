from pathlib import Path

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestTypecheck:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["typecheck"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="ty") in get_deps_from_group("dev")

    def test_how_option(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["typecheck", "--how"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "☐ Run 'ty check' to run the ty type checker.\n"

    def test_add_then_remove(self, tmp_path: Path):
        # Arrange
        runner = CliRunner()

        with change_cwd(tmp_path):
            # Act: Add typecheck
            result = runner.invoke_safe(app, ["typecheck"])
            assert result.exit_code == 0, result.output

            # Act: Remove typecheck
            result = runner.invoke_safe(app, ["typecheck", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="ty") not in get_deps_from_group("dev")

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["typecheck", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "☐ Add the dev dependency 'ty'.\n"
            "✔ Writing 'ty.toml'.\n"
            "✔ Adding ty config to 'ty.toml'.\n"
            "☐ Run 'ty check' to run the ty type checker.\n"
        )

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["typecheck", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == (
            "☐ Add the dev dependency 'ty'.\n"
            "✔ Adding ty config to 'pyproject.toml'.\n"
            "☐ Run 'ty check' to run the ty type checker.\n"
        )
