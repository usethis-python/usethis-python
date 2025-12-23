from pathlib import Path

import pytest

import usethis._integrations.python.version
from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app as main_app
from usethis._ui.interface.ci import app
from usethis._ui.interface.tool import ALL_TOOL_COMMANDS


class TestBitbucket:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app,  # The CI menu only has 1 command (bitbucket
                # pipelines) so we skip the subcommand here
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "bitbucket-pipelines.yml").exists()

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app, ["--remove"]
            )  # The CI menu only has 1 command (bitbucket
            # pipelines) so we skip the subcommand here

        # Assert
        assert result.exit_code == 0, result.output
        assert not (tmp_path / "bitbucket-pipelines.yml").exists()

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_maximal_config_uv(self, uv_init_repo_dir: Path):
        # N.B. uv_init_repo_dir is used since we need git if we want to add pre-commit
        runner = CliRunner()
        with change_cwd(uv_init_repo_dir):
            # Arrange
            with PyprojectTOMLManager() as mgr:
                mgr[["project"]]["requires-python"] = ">=3.12,<3.14"

            for tool_command in ALL_TOOL_COMMANDS:
                if not usethis_config.offline:
                    result = runner.invoke_safe(main_app, ["tool", tool_command])
                else:
                    result = runner.invoke_safe(
                        main_app, ["tool", tool_command, "--offline"]
                    )
                assert not result.exit_code, f"{tool_command=}: {result.stdout}"

            # Act
            result = runner.invoke_safe(
                app
            )  # The CI menu only has 1 command (bitbucket
            # pipelines) so we skip the subcommand here
            assert not result.exit_code, result.stdout

        # Assert
        expected_yml = (
            # N.B. when updating this file, check it against the validator:
            # https://bitbucket.org/product/pipelines/validator
            Path(__file__).parent / "maximal_bitbucket_pipelines_uv.yml"
        ).read_text()
        assert (
            uv_init_repo_dir / "bitbucket-pipelines.yml"
        ).read_text() == expected_yml

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_maximal_config_none_backend(
        self, bare_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Expected contents of a maximal config file using no backend.

        We don't use pre-commit for this test. This is mostly just to expand test
        coverage since the uv-based test does use pre-commit.
        """

        monkeypatch.setattr(
            usethis._integrations.python.version,
            "_get_python_version",
            lambda: "3.10.0",
        )

        runner = CliRunner()
        with change_cwd(bare_dir):
            # Arrange
            for tool_command in ALL_TOOL_COMMANDS:
                if tool_command == "pre-commit":
                    continue

                if not usethis_config.offline:
                    result = runner.invoke_safe(
                        main_app, ["tool", tool_command, "--backend=none"]
                    )
                else:
                    result = runner.invoke_safe(
                        main_app, ["tool", tool_command, "--offline", "--backend=none"]
                    )
                assert not result.exit_code, f"{tool_command=}: {result.stdout}"

            # Act
            result = runner.invoke_safe(
                app, "--backend=none"
            )  # The CI menu only has 1 command (bitbucket pipelines) so we skip the
            # subcommand here
            assert not result.exit_code, result.stdout

        # Assert
        expected_yml = (
            # N.B. when updating this file, check it against the validator:
            # https://bitbucket.org/product/pipelines/validator
            Path(__file__).parent / "maximal_bitbucket_pipelines_none_backend.yml"
        ).read_text()
        assert (bare_dir / "bitbucket-pipelines.yml").read_text() == expected_yml

    def test_invalid_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("(")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app)

        # Assert
        assert result.exit_code == 1, result.output

    def test_import_pipeline_error_handled(self, tmp_path: Path):
        """Test that import pipeline errors are handled gracefully at CLI level."""
        # Arrange - create a bitbucket-pipelines.yml with an import pipeline
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
        import: shared-pipeline:master:share-pipeline-1
"""
        )
        # Add a tool so update_bitbucket_steps gets called
        (tmp_path / "pytest.ini").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["--backend=none"])

        # Assert - error should be caught and handled, not propagate as unhandled exception
        assert result.exit_code == 1, result.output
        assert "import pipeline" in result.output.lower()

    def test_no_matrix_python_flag(
        self, uv_init_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --no-matrix-python flag creates single test step via CLI."""
        # Arrange
        monkeypatch.setattr(
            usethis._integrations.python.version,
            "_get_python_version",
            lambda: "3.10.0",
        )
        (uv_init_dir / "tests").mkdir()
        (uv_init_dir / "tests" / "conftest.py").touch()

        with PyprojectTOMLManager() as mgr:
            mgr[["project"]]["requires-python"] = ">=3.12,<3.14"

        # Act
        runner = CliRunner()
        with change_cwd(uv_init_dir):
            result = runner.invoke_safe(app, ["--no-matrix-python"])

        # Assert
        assert result.exit_code == 0, result.output
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        # Should only have one test step for the current development version (3.10)
        assert "Test on 3.10" in contents
        # Should NOT have other versions
        assert "Test on 3.12" not in contents
        assert "Test on 3.13" not in contents

    def test_matrix_python_flag_enabled_default(self, uv_init_dir: Path):
        """Test that --matrix-python (default) creates multiple test steps via CLI."""
        # Arrange
        (uv_init_dir / "tests").mkdir()
        (uv_init_dir / "tests" / "conftest.py").touch()

        with PyprojectTOMLManager() as mgr:
            mgr[["project"]]["requires-python"] = ">=3.12,<3.14"

        # Act
        runner = CliRunner()
        with change_cwd(uv_init_dir):
            result = runner.invoke_safe(app, ["--matrix-python"])

        # Assert
        assert result.exit_code == 0, result.output
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        # Should have multiple test steps
        assert "Test on 3.12" in contents
        assert "Test on 3.13" in contents
