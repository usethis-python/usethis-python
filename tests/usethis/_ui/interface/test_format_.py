from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._deps import get_deps_from_group
from usethis._test import CliRunner, change_cwd
from usethis._types.deps import Dependency
from usethis._ui.app import app


class TestFormat:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_dependencies_added(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            if not usethis_config.offline:
                result = runner.invoke_safe(app, ["format"])
            else:
                result = runner.invoke_safe(app, ["format", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        with change_cwd(tmp_path), files_manager():
            assert Dependency(name="ruff") in get_deps_from_group("dev")
            assert Dependency(name="pyproject-fmt") in get_deps_from_group("dev")

        # Check Ruff linter is not added
        txt = (tmp_path / "pyproject.toml").read_text()
        assert "ruff.lint" not in txt
        assert "ruff.format" in txt

    def test_none_backend_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["format", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Adding Ruff config to 'pyproject.toml'.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "☐ Add the dev dependency 'pyproject-fmt'.\n"
            "✔ Adding pyproject-fmt config to 'pyproject.toml'.\n"
            "☐ Run 'pyproject-fmt pyproject.toml' to run pyproject-fmt.\n"
        )

    def test_none_backend_no_pyproject_toml(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["format", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "☐ Add the dev dependency 'ruff'.\n"
            "✔ Writing 'ruff.toml'.\n"
            "✔ Adding Ruff config to 'ruff.toml'.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
        )
