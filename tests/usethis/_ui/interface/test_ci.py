from pathlib import Path

from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.ci import app


class TestBitbucket:
    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        assert result.output == (
            "⚠ 'usethis ci' is deprecated and will be removed in v0.20.0.\n"
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding placeholder step to default pipeline in 'bitbucket-pipelines.yml'.\n"
            "☐ Remove the placeholder pipeline step in 'bitbucket-pipelines.yml'.\n"
            "☐ Replace it with your own pipeline steps.\n"
            "☐ Alternatively, use 'usethis tool' to add other tools and their steps.\n"
            "ℹ Consider `usethis tool pytest` to test your code for the pipeline.\n"  # noqa: RUF001
            "☐ Run your pipeline via the Bitbucket website.\n"
        )
