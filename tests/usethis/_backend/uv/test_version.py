from pathlib import Path

import pytest

from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._backend.uv.version import get_uv_version, next_breaking_uv_version
from usethis._fallback import FALLBACK_UV_VERSION
from usethis._test import change_cwd


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
        def mock_call_uv_subprocess(*_: object, **__: object) -> str:
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            "usethis._backend.uv.version.call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        version = get_uv_version()

        # Assert
        assert version == FALLBACK_UV_VERSION


class TestNextBreakingUVVersion:
    def test_pre_one_bumps_minor(self):
        # Act
        result = next_breaking_uv_version("0.10.2")

        # Assert
        assert result == "0.11.0"

    def test_post_one_bumps_major(self):
        # Act
        result = next_breaking_uv_version("1.0.2")

        # Assert
        assert result == "2.0.0"

    def test_pre_one_zero_minor(self):
        # Act
        result = next_breaking_uv_version("0.0.5")

        # Assert
        assert result == "0.1.0"

    def test_exact_one(self):
        # Act
        result = next_breaking_uv_version("1.0.0")

        # Assert
        assert result == "2.0.0"

    def test_high_major(self):
        # Act
        result = next_breaking_uv_version("3.2.1")

        # Assert
        assert result == "4.0.0"
