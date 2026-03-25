from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._test import CliRunner, change_cwd
from usethis._types.backend import BackendEnum
from usethis._ui.interface.show import app


class TestBackend:
    def test_uv_backend(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.lock").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["backend"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "uv\n"

    def test_none_backend(self, tmp_path: Path):
        # Arrange

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
            result = runner.invoke_safe(app, ["backend"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "none\n"


class TestName:
    def test_output(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "fun"
        path.mkdir()

        # Act
        runner = CliRunner()
        with change_cwd(path):
            result = runner.invoke_safe(app, ["name"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == """fun\n"""

    def test_invalid_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["name"])

        # Assert
        assert result.exit_code == 1, result.output


class TestSonarqube:
    def test_runs(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.usethis.sonarqube]
project-key = "fun"

[tool.coverage.xml.output]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output

    def test_missing_key(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 1, result.output

    def test_project_key_option(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.coverage.xml.output]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["sonarqube", "--project-key", "my-project"]
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert "sonar.projectKey=my-project" in result.output

    def test_project_key_option_overrides_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.usethis.sonarqube]
project-key = "from-pyproject"

[tool.coverage.xml.output]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube", "--project-key", "from-cli"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "sonar.projectKey=from-cli" in result.output

    def test_project_key_option_invalid(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.coverage.xml.output]
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["sonarqube", "--project-key", "invalid key!"]
            )

        # Assert
        assert result.exit_code == 1, result.output

    def test_invalid_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 1, result.output


class TestImportLinter:
    def test_toml_format(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        (tmp_path / "mypkg").mkdir()
        (tmp_path / "mypkg" / "__init__.py").touch()
        (tmp_path / "mypkg" / "a.py").touch()
        (tmp_path / "mypkg" / "b.py").write_text("import mypkg.a\n")
        (tmp_path / "mypkg" / "c.py").write_text("import mypkg.a\nimport mypkg.b\n")
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "toml"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "[tool.importlinter]" in result.output
        assert "root_packages" in result.output
        assert "[[tool.importlinter.contracts]]" in result.output
        assert '"mypkg"' in result.output

    def test_ini_format(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        (tmp_path / "mypkg").mkdir()
        (tmp_path / "mypkg" / "__init__.py").touch()
        (tmp_path / "mypkg" / "a.py").touch()
        (tmp_path / "mypkg" / "b.py").write_text("import mypkg.a\n")
        (tmp_path / "mypkg" / "c.py").write_text("import mypkg.a\nimport mypkg.b\n")
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "ini"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "[importlinter]" in result.output
        assert "root_package = mypkg" in result.output
        assert "[importlinter:contract:0]" in result.output

    def test_toml_multiple_packages(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\nversion = "0.1.0"\n'
        )
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").touch()
        (tmp_path / "b").mkdir()
        (tmp_path / "b" / "__init__.py").touch()
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "toml"])

        # Assert
        assert result.exit_code == 0, result.output
        assert 'root_packages = ["a", "b"]' in result.output

    def test_ini_multiple_packages(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\nversion = "0.1.0"\n'
        )
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").touch()
        (tmp_path / "b").mkdir()
        (tmp_path / "b" / "__init__.py").touch()
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "ini"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "root_packages =" in result.output
        assert "    a" in result.output
        assert "    b" in result.output

    def test_toml_contract_content(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "mypkg").mkdir()
        (tmp_path / "mypkg" / "__init__.py").touch()
        (tmp_path / "mypkg" / "a.py").touch()
        (tmp_path / "mypkg" / "b.py").write_text("import mypkg.a\n")
        (tmp_path / "mypkg" / "c.py").write_text("import mypkg.a\nimport mypkg.b\n")
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "toml"])

        # Assert
        assert result.exit_code == 0, result.output
        assert 'name = "mypkg"' in result.output
        assert 'type = "layers"' in result.output
        assert "exhaustive = true" in result.output

    def test_ini_contract_content(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "mypkg").mkdir()
        (tmp_path / "mypkg" / "__init__.py").touch()
        (tmp_path / "mypkg" / "a.py").touch()
        (tmp_path / "mypkg" / "b.py").write_text("import mypkg.a\n")
        (tmp_path / "mypkg" / "c.py").write_text("import mypkg.a\nimport mypkg.b\n")
        monkeypatch.syspath_prepend(str(tmp_path))

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["import-linter", "--format", "ini"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "name = mypkg" in result.output
        assert "type = layers" in result.output
        assert "exhaustive = True" in result.output
