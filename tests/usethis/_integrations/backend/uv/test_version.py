import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._integrations.backend.uv.errors import UVSubprocessFailedError
from usethis._integrations.backend.uv.version import FALLBACK_UV_VERSION, get_uv_version
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._test import change_cwd


class TestGetUVVersion:
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
            if (
                usethis_config.offline
                or "rate limit exceeded for url" in str(err)
                or "Read timed out." in str(err)
            ):
                pytest.skip(
                    "Failed to fetch GitHub tags (connection issues); skipping test"
                )
            raise err

    def test_matches_pattern(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            version = get_uv_version()

        # Assert
        assert isinstance(version, str)
        assert version.count(".") == 2
        major, minor, patch = version.split(".")
        assert major.isdigit()
        assert minor.isdigit()
        assert patch.isdigit()

    def test_mock_subprocess_failure(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_call_uv_subprocess(*_, **__) -> str:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            "usethis._integrations.backend.uv.version.call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        version = get_uv_version()

        # Assert
        assert version == FALLBACK_UV_VERSION
