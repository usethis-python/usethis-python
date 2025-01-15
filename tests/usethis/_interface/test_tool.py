from pathlib import Path

import pytest
from typer.testing import CliRunner

from usethis._interface.tool import app
from usethis._test import change_cwd


class TestPytest:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["pytest"])

        # Assert
        assert result.exit_code == 0


@pytest.mark.benchmark
def test_several_tools_add_and_remove(tmp_path: Path):
    runner = CliRunner()
    with change_cwd(tmp_path):
        runner.invoke(app, ["pytest"])
        runner.invoke(app, ["ruff"])
        runner.invoke(app, ["deptry"])
        runner.invoke(app, ["pre-commit"])
        runner.invoke(app, ["ruff", "--remove"])
        runner.invoke(app, ["pyproject-fmt"])
        runner.invoke(app, ["pytest", "--remove"])
