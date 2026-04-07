from pathlib import Path

import pytest

from _test import CliRunner, change_cwd
from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._ui.interface.show import app

_MIT_LICENSE_TEXT = """\
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


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

    def test_output_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.lock").touch()
        output_file = tmp_path / "backend.txt"

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["backend", "--output-file", str(output_file)]
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert output_file.read_text(encoding="utf-8") == "uv\n"


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

    def test_output_file(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "fun"
        path.mkdir()
        output_file = path / "name.txt"

        # Act
        runner = CliRunner()
        with change_cwd(path):
            result = runner.invoke_safe(
                app, ["name", "--output-file", str(output_file)]
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert output_file.read_text(encoding="utf-8") == "fun\n"


class TestLicense:
    def test_from_license_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["license"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "MIT\n"

    def test_from_pyproject_field(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = "Apache-2.0"\n'
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["license"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output == "Apache-2.0\n"

    def test_no_license(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["license"])

        # Assert
        assert result.exit_code == 1, result.output

    def test_output_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)
        output_file = tmp_path / "license.txt"

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["license", "--output-file", str(output_file)]
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert output_file.read_text(encoding="utf-8") == "MIT\n"


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

    def test_env_var_project_key(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # SONAR_PROJECT_KEY env var is used when --project-key is not provided.

        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.coverage.xml.output]
"""
        )
        monkeypatch.setenv("SONAR_PROJECT_KEY", "from-env")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 0, result.output
        assert "sonar.projectKey=from-env" in result.output

    def test_invalid_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["sonarqube"])

        # Assert
        assert result.exit_code == 1, result.output

    def test_output_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.usethis.sonarqube]
project-key = "fun"

[tool.coverage.xml.output]
"""
        )
        output_file = tmp_path / "sonar-project.properties"

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["sonarqube", "--output-file", str(output_file)]
            )

        # Assert
        assert result.exit_code == 0, result.output
        content = output_file.read_text(encoding="utf-8")
        assert "sonar.projectKey=fun" in content

    def test_output_file_not_detected_as_existing(self, tmp_path: Path):
        """Using --output-file avoids the redirect problem.

        When using shell redirect (`> file`), the file is created empty before
        the command runs, which causes sonarqube to read that empty file.
        With --output-file, the file is written after generation.
        """
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.usethis.sonarqube]
project-key = "fun"

[tool.coverage.xml.output]
"""
        )
        # Simulate what happens with shell redirect: an empty file pre-exists
        output_file = tmp_path / "sonar-project.properties"
        output_file.write_text("", encoding="utf-8")

        # Act
        # Despite sonar-project.properties existing (empty), --output-file
        # still causes the config to be read from that file (by design of
        # get_sonar_project_properties), then overwrites it with that content.
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["sonarqube", "--output-file", str(output_file)]
            )

        # Assert
        assert result.exit_code == 0, result.output
        content = output_file.read_text(encoding="utf-8")
        # With --output-file, the file is written after content generation,
        # so even if it was previously empty, it will have the content now
        assert content != ""
