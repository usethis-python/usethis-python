from pathlib import Path

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestTest:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["test"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="pytest") in get_deps_from_group("test")

    def test_none_backend_no_pyproject_toml(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["test", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "☐ Add the test dependency 'pytest'.\n"
            "✔ Writing 'pytest.ini'.\n"
            "✔ Adding pytest config to 'pytest.ini'.\n"
            "✔ Creating '/tests'.\n"
            "✔ Writing '/tests/conftest.py'.\n"
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Run 'pytest' to run the tests.\n"
            "☐ Add the test dependencies 'coverage', 'pytest-cov'.\n"
            "✔ Writing '.coveragerc'.\n"
            "✔ Adding Coverage.py config to '.coveragerc'.\n"
            "☐ Run 'pytest --cov' to run your tests with Coverage.py.\n"
        )

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["test", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "☐ Add the test dependency 'pytest'.\n"
            "✔ Adding pytest config to 'pyproject.toml'.\n"
            "✔ Creating '/tests'.\n"
            "✔ Writing '/tests/conftest.py'.\n"
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Run 'pytest' to run the tests.\n"
            "☐ Add the test dependencies 'coverage', 'pytest-cov'.\n"
            "✔ Adding Coverage.py config to 'pyproject.toml'.\n"
            "☐ Run 'pytest --cov' to run your tests with Coverage.py.\n"
        )
