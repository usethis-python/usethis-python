from pathlib import Path

import pytest
from typer.testing import CliRunner

from usethis._app import app
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.uv.deps import Dependency, get_deps_from_group
from usethis._test import change_cwd


class TestDoc:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            if not usethis_config.offline:
                result = runner.invoke(app, ["doc"])
            else:
                result = runner.invoke(app, ["doc", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="mkdocs") in get_deps_from_group("doc")
