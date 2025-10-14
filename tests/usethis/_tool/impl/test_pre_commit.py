import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit.schema import UriRepo
from usethis._test import change_cwd
from usethis._tool.impl.pre_commit import PreCommitTool


class TestPreCommitTool:
    class TestIsUsed:
        def test_pre_commit_config_file(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").touch()

            # Act, Assert
            with change_cwd(tmp_path):
                assert PreCommitTool().is_used()

        def test_pre_commit_disabled(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").touch()

            # Act, Assert
            with change_cwd(tmp_path), usethis_config.set(disable_pre_commit=True):
                assert not PreCommitTool().is_used()

        def test_empty_dir(self, tmp_path: Path):
            # Act, Assert
            with change_cwd(tmp_path), files_manager():
                assert not PreCommitTool().is_used()

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        (config,) = PreCommitTool().get_pre_commit_config().repo_configs
        repo = config.repo
        assert isinstance(repo, UriRepo)
        try:
            assert repo.rev == get_github_latest_tag(
                owner="tsvikas", repo="sync-with-uv"
            )
        except GitHubTagError as err:
            if usethis_config.offline or "rate limit exceeded for url" in str(err):
                pytest.skip(
                    "Failed to fetch GitHub tags (connection issues); skipping test"
                )
            raise err
