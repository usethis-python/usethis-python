from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestDoc:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            if not usethis_config.offline:
                result = runner.invoke_safe(app, ["doc"])
            else:
                result = runner.invoke_safe(app, ["doc", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="mkdocs") in get_deps_from_group("doc")
