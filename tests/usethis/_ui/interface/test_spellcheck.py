from pathlib import Path

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._python.version import PythonVersion
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestSpellcheck:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["spellcheck"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="codespell") in get_deps_from_group("dev")

    def test_how_option(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["spellcheck", "--how"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "☐ Run 'codespell' to run the Codespell spellchecker.\n"

    def test_add_then_remove(self, tmp_path: Path):
        # Arrange
        runner = CliRunner()

        with change_cwd(tmp_path):
            # Act: Add spellcheck
            result = runner.invoke_safe(app, ["spellcheck"])
            assert result.exit_code == 0, result.output

            # Act: Remove spellcheck
            result = runner.invoke_safe(app, ["spellcheck", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="codespell") not in get_deps_from_group("dev")

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["spellcheck", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "pyproject.toml").exists()
        # Check if tomli is needed based on current interpreter
        current_version = PythonVersion.from_interpreter()
        needs_tomli = current_version.to_short_tuple() < (3, 11)
        if needs_tomli:
            expected_deps = "☐ Add the dev dependencies 'codespell', 'tomli'.\n"
        else:
            expected_deps = "☐ Add the dev dependency 'codespell'.\n"
        assert result.output == (
            expected_deps + "✔ Writing '.codespellrc'.\n"
            "✔ Adding Codespell config to '.codespellrc'.\n"
            "☐ Run 'codespell' to run the Codespell spellchecker.\n"
        )

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["spellcheck", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        # Check if tomli is needed based on current interpreter
        current_version = PythonVersion.from_interpreter()
        needs_tomli = current_version.to_short_tuple() < (3, 11)
        if needs_tomli:
            expected_deps = "☐ Add the dev dependencies 'codespell', 'tomli'.\n"
        else:
            expected_deps = "☐ Add the dev dependency 'codespell'.\n"
        assert result.output == (
            expected_deps + "✔ Adding Codespell config to 'pyproject.toml'.\n"
            "☐ Run 'codespell' to run the Codespell spellchecker.\n"
        )
