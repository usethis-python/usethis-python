from pathlib import Path

from typer.testing import CliRunner

from usethis._app import app as main_app
from usethis._interface.ci import app
from usethis._interface.tool import ALL_TOOL_COMMANDS
from usethis._test import change_cwd


class TestBitbucket:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(
                app,  # The CI menu only has 1 command (bitbucket
                # pipelines) so we skip the subcommand here
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "bitbucket-pipelines.yml").exists()

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(
                app, ["--remove"]
            )  # The CI menu only has 1 command (bitbucket
            # pipelines) so we skip the subcommand here

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "bitbucket-pipelines.yml").exists()

    def test_maximal_config(self, tmp_path: Path):
        runner = CliRunner()
        with change_cwd(tmp_path):
            # Arrange
            for tool_command in ALL_TOOL_COMMANDS:
                runner.invoke(main_app, ["tool", tool_command])

            # Act
            runner.invoke(app)  # The CI menu only has 1 command (bitbucket
            # pipelines) so we skip the subcommand here

        # Assert
        expected_yml = (
            Path(__file__).parent / "maximal_bitbucket_pipelines.yml"
        ).read_text()
        assert (tmp_path / "bitbucket-pipelines.yml").read_text() == expected_yml
