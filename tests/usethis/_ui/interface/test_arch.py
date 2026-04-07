from pathlib import Path

from _test import CliRunner, change_cwd
from usethis._ui.app import app


class TestArch:
    def test_how_option(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["arch", "--how"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "lint-imports" in result.output

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\n\n[tool.usethis]\n'
        )
        (tmp_path / "src" / "myproject").mkdir(parents=True)
        (tmp_path / "src" / "myproject" / "__init__.py").touch()
        (tmp_path / "src" / "myproject" / "a.py").touch()
        (tmp_path / "src" / "myproject" / "b.py").touch()
        (tmp_path / "src" / "myproject" / "c.py").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["arch", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "☐ Add the dev dependency 'import-linter'." in result.output
        assert "Adding Import Linter config to 'pyproject.toml'." in result.output
        assert "lint-imports" in result.output

    def test_add_then_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\n\n[tool.usethis]\n'
        )
        (tmp_path / "src" / "myproject").mkdir(parents=True)
        (tmp_path / "src" / "myproject" / "__init__.py").touch()
        (tmp_path / "src" / "myproject" / "a.py").touch()
        (tmp_path / "src" / "myproject" / "b.py").touch()
        (tmp_path / "src" / "myproject" / "c.py").touch()

        runner = CliRunner()

        with change_cwd(tmp_path):
            # Act: Add arch
            result = runner.invoke_safe(app, ["arch", "--backend", "none"])
            assert result.exit_code == 0, result.output

            # Act: Remove arch
            result = runner.invoke_safe(app, ["arch", "--remove", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "Removing" in result.output
