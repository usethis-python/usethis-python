from pathlib import Path

import pytest

from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._backend.uv.version import get_uv_version
from usethis._test import change_cwd
from usethis._versions import FALLBACK_UV_VERSION


class TestGetUVVersion:
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
            "usethis._backend.uv.version.call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        version = get_uv_version()

        # Assert
        assert version == FALLBACK_UV_VERSION
