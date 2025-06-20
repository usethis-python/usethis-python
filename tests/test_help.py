import pytest
from typer.testing import CliRunner

from usethis._interface.tool import app


@pytest.mark.benchmark
def test_help_flag():
    # Arrange
    runner = CliRunner()

    # Act
    runner.invoke(app, ["--help"])
