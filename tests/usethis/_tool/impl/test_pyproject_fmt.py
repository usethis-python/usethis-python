import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit.schema import UriRepo
from usethis._test import change_cwd
from usethis._tool.impl.pyproject_fmt import PyprojectFmtTool


class TestPyprojectFmtTool:
    class TestPrintHowToUse:
        def test_uv_only(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                PyprojectFmtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'uv run pyproject-fmt pyproject.toml' to run pyproject-fmt.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        (config,) = PyprojectFmtTool().get_pre_commit_config().repo_configs
        repo = config.repo
        assert isinstance(repo, UriRepo)
        try:
            assert repo.rev == get_github_latest_tag(
                owner="tox-dev", repo="pyproject-fmt"
            )
        except GitHubTagError as err:
            if usethis_config.offline or "rate limit exceeded for url" in str(err):
                pytest.skip(
                    "Failed to fetch GitHub tags (connection issues); skipping test"
                )
            raise err
