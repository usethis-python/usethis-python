import os

import pytest

from usethis._config import usethis_config
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._versions import (
    CODESPELL_VERSION,
    FALLBACK_UV_VERSION,
    PRE_COMMIT_VERSION,
    PYPROJECT_FMT_VERSION,
    RUFF_VERSION,
    SYNC_WITH_UV_VERSION,
)


def _skip_on_github_error(err: GitHubTagError) -> None:
    if (
        usethis_config.offline
        or "rate limit exceeded for url" in str(err)
        or "Read timed out." in str(err)
    ):
        pytest.skip("Failed to fetch GitHub tags (connection issues); skipping test")


class TestFallbackUVVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="astral-sh", repo="uv")
                == FALLBACK_UV_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestPreCommitVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="pre-commit", repo="pre-commit")
                == f"v{PRE_COMMIT_VERSION}"
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestRuffVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="astral-sh", repo="ruff-pre-commit")
                == RUFF_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestSyncWithUVVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="tsvikas", repo="sync-with-uv")
                == SYNC_WITH_UV_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestCodespellVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="codespell-project", repo="codespell")
                == CODESPELL_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestPyprojectFmtVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            # N.B. this is the pre-commit mirror, it can lag behind the main repo
            # at https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt
            assert (
                get_github_latest_tag(owner="tox-dev", repo="pyproject-fmt")
                == PYPROJECT_FMT_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err
