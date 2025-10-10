from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.ci import app


class TestBitbucket:
    def test_readme_example(self, tmp_path: Path):
        """This example is used the README.md file.

        Note carefully! If this test is updated, the README.md file must be
        updated too.
        """
        # Arrange
        # We've already run ruff and pytest...
        (tmp_path / "pytest.ini").touch()
        (tmp_path / "ruff.toml").touch()
        # Consistent versions in the matrix - only two to demonstrate it, 3 is excessive
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.12,<3.14"
"""
        )

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, [])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == """\
✔ Writing 'bitbucket-pipelines.yml'.
✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.
✔ Adding 'Run Ruff' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Run Ruff Formatter' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.12' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.13' to default pipeline in 'bitbucket-pipelines.yml'.
☐ Run your pipeline via the Bitbucket website.
"""
        )

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        assert result.output == (
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding placeholder step to default pipeline in 'bitbucket-pipelines.yml'.\n"
            "☐ Remove the placeholder pipeline step in 'bitbucket-pipelines.yml'.\n"
            "☐ Replace it with your own pipeline steps.\n"
            "☐ Alternatively, use 'usethis tool' to add other tools and their steps.\n"
            "ℹ Consider `usethis tool pytest` to test your code for the pipeline.\n"  # noqa: RUF001
            "☐ Run your pipeline via the Bitbucket website.\n"
        )
