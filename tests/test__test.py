from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from _test import is_uv_python_available


class TestIsUvPythonAvailable:
    def test_current_python_is_available(self):
        # The Python version currently running the test suite must be present
        # in uv's managed installations.
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert is_uv_python_available(version) is True

    def test_nonsense_version_returns_false(self):
        assert is_uv_python_available("99.99") is False

    def test_returns_false_when_uv_not_found(self):
        with patch("_test.shutil.which", return_value=None):
            assert is_uv_python_available("3.12") is False

    def test_version_matched_from_subprocess_output(self):
        mock_result = MagicMock()
        mock_result.stdout = "cpython-3.13.1-linux-x86_64-gnu    /usr/bin/python3.13\n"
        with (
            patch("_test.shutil.which", return_value="/usr/bin/uv"),
            patch("_test.subprocess.run", return_value=mock_result),
        ):
            assert is_uv_python_available("3.13") is True

    def test_version_not_matched_from_subprocess_output(self):
        mock_result = MagicMock()
        mock_result.stdout = "cpython-3.12.3-linux-x86_64-gnu    /usr/bin/python3.12\n"
        with (
            patch("_test.shutil.which", return_value="/usr/bin/uv"),
            patch("_test.subprocess.run", return_value=mock_result),
        ):
            assert is_uv_python_available("3.13") is False

    def test_empty_output_returns_false(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with (
            patch("_test.shutil.which", return_value="/usr/bin/uv"),
            patch("_test.subprocess.run", return_value=mock_result),
        ):
            assert is_uv_python_available("3.12") is False

    def test_partial_version_does_not_match(self):
        # "3.1" should not match "3.10.x" or "3.13.x"
        mock_result = MagicMock()
        mock_result.stdout = (
            "cpython-3.10.18-linux-x86_64-gnu    /home/runner/.uv/python3.10\n"
            "cpython-3.13.1-linux-x86_64-gnu     /home/runner/.uv/python3.13\n"
        )
        with (
            patch("_test.shutil.which", return_value="/usr/bin/uv"),
            patch("_test.subprocess.run", return_value=mock_result),
        ):
            assert is_uv_python_available("3.1") is False
