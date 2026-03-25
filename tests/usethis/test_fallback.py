import os

import pytest

from usethis._config import usethis_config
from usethis._fallback import (
    FALLBACK_CODESPELL_VERSION,
    FALLBACK_HATCHLING_VERSION,
    FALLBACK_PRE_COMMIT_VERSION,
    FALLBACK_PYPROJECT_FMT_VERSION,
    FALLBACK_RUFF_VERSION,
    FALLBACK_SYNC_WITH_UV_VERSION,
    FALLBACK_UV_VERSION,
    next_breaking_version,
)
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag


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


class TestFallbackHatchlingVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert (
                get_github_latest_tag(owner="pypa", repo="hatch")
                == f"hatchling-v{FALLBACK_HATCHLING_VERSION}"
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
                == f"v{FALLBACK_PRE_COMMIT_VERSION}"
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
                == FALLBACK_RUFF_VERSION
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
                == FALLBACK_SYNC_WITH_UV_VERSION
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
                == FALLBACK_CODESPELL_VERSION
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
                == FALLBACK_PYPROJECT_FMT_VERSION
            )
        except GitHubTagError as err:
            _skip_on_github_error(err)
            raise err


class TestNextBreakingVersion:
    def test_pre_one_bumps_minor(self):
        assert next_breaking_version("0.10.2") == "0.11.0"

    def test_post_one_bumps_major(self):
        assert next_breaking_version("1.0.2") == "2.0.0"

    def test_pre_one_zero_minor(self):
        assert next_breaking_version("0.0.5") == "0.1.0"

    def test_exact_one(self):
        assert next_breaking_version("1.0.0") == "2.0.0"

    def test_high_major(self):
        assert next_breaking_version("3.2.1") == "4.0.0"
