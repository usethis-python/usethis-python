import pytest
from rich.table import Table

from usethis._console import (
    box_print,
    err_print,
    info_print,
    plain_print,
    table_print,
    tick_print,
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
