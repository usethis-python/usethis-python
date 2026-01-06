import sys
from unittest.mock import Mock

import pytest
from rich.table import Table

from usethis._config import usethis_config
from usethis._console import (
    _get_icon,
    _get_stdout_encoding,
    err_print,
    get_icon_mode,
    how_print,
    info_print,
    instruct_print,
    plain_print,
    table_print,
    tick_print,
    warn_print,
)


class TestPlainPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        plain_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "Hello\n"


class TestTablePrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        table_print(
            Table(
                "hello",
                title="Hello",
                show_lines=True,
                box=None,
            )
        )

        # Assert
        out, _ = capfd.readouterr()
        assert "hello" in out
        assert "Hello" in out


class TestTickPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        tick_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Hello\n"

    def test_alert_only_suppresses(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        with usethis_config.set(alert_only=True):
            tick_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert not out

    def test_instruct_only_suppresses(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        with usethis_config.set(instruct_only=True):
            tick_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert not out


class TestInstructPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        instruct_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "☐ Hello\n"

    def test_instruct_only_does_not_suppress(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        with usethis_config.set(instruct_only=True):
            instruct_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "☐ Hello\n"


class TestHowPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        how_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "☐ Hello\n"

    def test_instruct_only_suppresses(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        with usethis_config.set(instruct_only=True):
            how_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert not out


class TestInfoPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        info_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "ℹ Hello\n"  # noqa: RUF001


class TestErrPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        err_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not out
        assert err == "✗ Hello\n"

    def test_alert_only_doesnt_suppress(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        with usethis_config.set(alert_only=False):
            err_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert err == "✗ Hello\n"
        assert not out


class TestWarnPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        warn_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "⚠ Hello\n"

    def test_alert_only_doesnt_suppress(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        with usethis_config.set(alert_only=False):
            warn_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "⚠ Hello\n"

    def test_cached_str(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        warn_print("Hello")
        warn_print("Hello")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "⚠ Hello\n"

    def test_cached_exception(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        warn_print(Exception("Hello"))
        warn_print(Exception("Hello"))

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "⚠ Hello\n"


class TestGetIconMode:
    def test_unicode_support(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "utf-8")
        get_icon_mode.cache_clear()

        # Act
        mode = get_icon_mode()

        # Assert
        assert mode == "unicode"

    def test_universal_support(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange - use cp437 which supports universal but not unicode icons
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "cp437")
        get_icon_mode.cache_clear()

        # Act
        mode = get_icon_mode()

        # Assert
        assert mode == "universal"

    def test_text_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "ascii")
        get_icon_mode.cache_clear()

        # Act
        mode = get_icon_mode()

        # Assert
        assert mode == "text"

    def test_no_encoding_defaults_utf8(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange - _get_encoding returns utf-8 when stdout.encoding is None
        mock_stdout = Mock()
        mock_stdout.encoding = None
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        get_icon_mode.cache_clear()

        # Act
        encoding = _get_stdout_encoding()
        mode = get_icon_mode()

        # Assert
        assert encoding == "utf-8"
        assert mode == "unicode"


class TestGetIcon:
    def test_unicode_mode_returns_unicode_icons(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "utf-8")
        get_icon_mode.cache_clear()

        # Act & Assert
        assert _get_icon("tick") == "✔"
        assert _get_icon("instruct") == "☐"
        assert _get_icon("how") == "☐"
        assert _get_icon("info") == "ℹ"  # noqa: RUF001
        assert _get_icon("error") == "✗"
        assert _get_icon("warning") == "⚠"

    def test_universal_mode_returns_universal_icons(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "cp437")
        get_icon_mode.cache_clear()

        # Act & Assert
        assert _get_icon("tick") == "√"
        assert _get_icon("instruct") == "□"
        assert _get_icon("how") == "□"
        assert _get_icon("info") == "i"
        assert _get_icon("error") == "×"  # noqa: RUF001
        assert _get_icon("warning") == "!"

    def test_text_mode_returns_text_labels(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "ascii")
        get_icon_mode.cache_clear()

        # Act & Assert
        # Note: Icons have escaped brackets for Rich console
        assert _get_icon("tick") == "\\[ok]"
        assert _get_icon("instruct") == "\\[todo]"
        assert _get_icon("how") == "\\[todo]"
        assert _get_icon("info") == "\\[info]"
        assert _get_icon("error") == "\\[error]"
        assert _get_icon("warning") == "\\[warning]"


class TestIconFallbackIntegration:
    """Test that print functions work with different icon modes."""

    def test_tick_print_with_text_mode(
        self, capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "ascii")
        get_icon_mode.cache_clear()

        # Act
        tick_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert "[ok] Hello\n" in out

    def test_warn_print_with_universal_mode(
        self, capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setattr("usethis._console._get_encoding", lambda: "cp437")
        get_icon_mode.cache_clear()

        # Act
        warn_print("Warning message")

        # Assert
        out, _ = capfd.readouterr()
        assert "! Warning message\n" in out
