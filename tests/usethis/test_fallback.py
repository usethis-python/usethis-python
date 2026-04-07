import os

import pytest

from _test import GitHubTagError, get_github_latest_tag
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


def _skip_on_github_error(err: GitHubTagError) -> None:
    if (
        usethis_config.offline
        or "rate limit exceeded for url" in str(err)
        or "Read timed out." in str(err)
    ):
        pytest.skip("Failed to fetch GitHub tags (connection issues); skipping test")


class TestLatestVersion:
    @pytest.mark.usefixtures("_vary_network_conn")
    @pytest.mark.parametrize(
        ("owner", "repo", "expected_tag"),
        [
            ("astral-sh", "uv", FALLBACK_UV_VERSION),
            ("pypa", "hatch", f"hatchling-v{FALLBACK_HATCHLING_VERSION}"),
            ("pre-commit", "pre-commit", f"v{FALLBACK_PRE_COMMIT_VERSION}"),
            ("astral-sh", "ruff-pre-commit", FALLBACK_RUFF_VERSION),
            ("tsvikas", "sync-with-uv", FALLBACK_SYNC_WITH_UV_VERSION),
            ("codespell-project", "codespell", FALLBACK_CODESPELL_VERSION),
            # N.B. this is the pre-commit mirror, it can lag behind the main repo
            # at https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt
            ("tox-dev", "pyproject-fmt", FALLBACK_PYPROJECT_FMT_VERSION),
        ],
        ids=[
            "uv",
            "hatchling",
            "pre-commit",
            "ruff",
            "sync-with-uv",
            "codespell",
            "pyproject-fmt",
        ],
    )
    def test_latest_version(self, owner: str, repo: str, expected_tag: str):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        try:
            assert get_github_latest_tag(owner=owner, repo=repo) == expected_tag
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
