import pytest

from usethis._console import box_print, err_print, info_print, tick_print


class TestTickPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        tick_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Hello\n"


class TestBoxPrint:
    def test_out(self, capfd: pytest.CaptureFixture[str]) -> None:
        # Act
        box_print("Hello")

        # Assert
        out, _ = capfd.readouterr()
        assert out == "☐ Hello\n"


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
        out, _ = capfd.readouterr()
        assert out == "✗ Hello\n"
