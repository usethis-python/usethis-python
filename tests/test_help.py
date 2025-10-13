import pytest

from usethis._test import CliRunner
from usethis._ui.interface.tool import app


@pytest.mark.benchmark
def test_help_flag():
    # Arrange
    runner = CliRunner()

    # Act
    result = runner.invoke_safe(app, ["--help"])
    assert result.exit_code == 0, result.stdout
