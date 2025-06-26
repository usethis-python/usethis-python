import pytest
from typer.testing import CliRunner

from usethis._interface.tool import app


@pytest.mark.benchmark
def test_help_flag():
    # Arrange
    runner = CliRunner()

    # Act
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.stdout
