from pathlib import Path

from typer.testing import CliRunner

from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestTest:
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["test"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="pytest") in get_deps_from_group("test")
