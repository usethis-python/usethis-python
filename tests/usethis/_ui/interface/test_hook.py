from pathlib import Path

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestHook:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["hook"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="pre-commit") in get_deps_from_group("dev")

    def test_how_option(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["hook", "--how"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "pre-commit" in result.output

    def test_add_then_remove(self, tmp_path: Path):
        # Arrange
        runner = CliRunner()

        with change_cwd(tmp_path):
            # Act: Add hook framework
            result = runner.invoke_safe(app, ["hook"])
            assert result.exit_code == 0, result.output

            # Act: Remove hook framework
            result = runner.invoke_safe(app, ["hook", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="pre-commit") not in get_deps_from_group("dev")

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["hook", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "pre-commit" in result.output
