from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._integrations.pre_commit.hooks import get_hook_ids
from usethis._test import CliRunner, change_cwd
from usethis._ui.app import app


class TestInit:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pre_commit_included(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            if not usethis_config.offline:
                result = runner.invoke_safe(app, ["init", "--pre-commit"])
            else:
                result = runner.invoke_safe(app, ["init", "--pre-commit", "--offline"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "✔ Writing 'pyproject.toml' and initializing project.\n"
            "✔ Writing 'README.md'.\n"
            "☐ Populate 'README.md' to help users understand the project.\n"
            "✔ Setting the development status to '1 - Planning'.\n"
            "✔ Adding the pre-commit framework.\n"
            "☐ Run 'uv run pre-commit run --all-files' to run the hooks manually.\n"
            "✔ Adding recommended documentation tools.\n"
            "☐ Run 'uv run mkdocs build' to build the documentation.\n"
            "☐ Run 'uv run mkdocs serve' to serve the documentation locally.\n"
            "✔ Adding recommended linters.\n"
            "☐ Run 'uv run deptry src' to run deptry.\n"
            "☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.\n"
            "✔ Adding recommended formatters.\n"
            "☐ Run 'uv run ruff format' to run the Ruff formatter.\n"
            "☐ Run 'uv run pre-commit run pyproject-fmt --all-files' to run pyproject-fmt.\n"
            "✔ Adding recommended spellcheckers.\n"
            "☐ Run 'uv run pre-commit run codespell --all-files' to run the Codespell \n"
            "spellchecker.\n"
            "✔ Adding recommended test frameworks.\n"
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Run 'uv run pytest' to run the tests.\n"
            "☐ Run 'uv run pytest --cov' to run your tests with Coverage.py.\n"
        )

        # Check the pre-commit hooks are added in the correct order
        with change_cwd(tmp_path):
            hook_ids = get_hook_ids()
            assert hook_ids == [
                "sync-with-uv",
                "pyproject-fmt",
                "ruff-check",
                "ruff-format",
                "deptry",
                "codespell",
            ]

    def test_readme_example(self, tmp_path: Path):
        """This example is used the README.md file.

        Note carefully! If this test is updated, the README.md file must be
        updated too.
        """
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["init"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            # ###################################
            # See docstring!
            # ###################################
            == """\
✔ Writing 'pyproject.toml' and initializing project.
✔ Writing 'README.md'.
☐ Populate 'README.md' to help users understand the project.
✔ Setting the development status to '1 - Planning'.
✔ Adding recommended documentation tools.
☐ Run 'uv run mkdocs build' to build the documentation.
☐ Run 'uv run mkdocs serve' to serve the documentation locally.
✔ Adding recommended linters.
☐ Run 'uv run deptry src' to run deptry.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
✔ Adding recommended formatters.
☐ Run 'uv run ruff format' to run the Ruff formatter.
☐ Run 'uv run pyproject-fmt pyproject.toml' to run pyproject-fmt.
✔ Adding recommended spellcheckers.
☐ Run 'uv run codespell' to run the Codespell spellchecker.
✔ Adding recommended test frameworks.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
☐ Run 'uv run pytest --cov' to run your tests with Coverage.py.
"""
        )

    def test_specify_path(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["init", "myproject"])

        # Assert
        assert result.exit_code == 0, result.output
        assert result.output.startswith(
            "☐ Change the current working directory to the project directory.\n"
        )

    def test_no_err_when_pyproject_toml_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["init"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_bitbucket_docstyle_and_status(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(
                app,
                [
                    "init",
                    "--ci",
                    "bitbucket",
                    "--docstyle",
                    "numpy",
                    "--pre-commit",
                    "--status",
                    "production",
                ],
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "✔ Writing 'pyproject.toml' and initializing project.\n"
            "✔ Writing 'README.md'.\n"
            "☐ Populate 'README.md' to help users understand the project.\n"
            "✔ Setting the development status to '5 - Production/Stable'.\n"
            "✔ Adding the pre-commit framework.\n"
            "☐ Run 'uv run pre-commit run --all-files' to run the hooks manually.\n"
            "✔ Adding recommended documentation tools.\n"
            "☐ Run 'uv run mkdocs build' to build the documentation.\n"
            "☐ Run 'uv run mkdocs serve' to serve the documentation locally.\n"
            "✔ Adding recommended linters.\n"
            "☐ Run 'uv run deptry src' to run deptry.\n"
            "☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.\n"
            "✔ Adding recommended formatters.\n"
            "☐ Run 'uv run ruff format' to run the Ruff formatter.\n"
            "☐ Run 'uv run pre-commit run pyproject-fmt --all-files' to run pyproject-fmt.\n"
            "✔ Setting docstring style to numpy.\n"
            "✔ Adding recommended spellcheckers.\n"
            "☐ Run 'uv run pre-commit run codespell --all-files' to run the Codespell \n"
            "spellchecker.\n"
            "✔ Adding recommended test frameworks.\n"
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Run 'uv run pytest' to run the tests.\n"
            "☐ Run 'uv run pytest --cov' to run your tests with Coverage.py.\n"
            "✔ Adding Bitbucket Pipelines configuration.\n"
            "☐ Run your pipeline via the Bitbucket website.\n"
        )

    def test_none_backend(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["init", "--backend", "none"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "✔ Writing 'pyproject.toml' and initializing project.\n"
            "✔ Writing 'README.md'.\n"
            "☐ Populate 'README.md' to help users understand the project.\n"
            "✔ Setting the development status to '1 - Planning'.\n"
            "✔ Adding recommended documentation tools.\n"
            "☐ Run 'mkdocs build' to build the documentation.\n"
            "☐ Run 'mkdocs serve' to serve the documentation locally.\n"
            "✔ Adding recommended linters.\n"
            "☐ Run 'deptry src' to run deptry.\n"
            "☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.\n"
            "✔ Adding recommended formatters.\n"
            "☐ Run 'ruff format' to run the Ruff formatter.\n"
            "☐ Run 'pyproject-fmt pyproject.toml' to run pyproject-fmt.\n"
            "✔ Adding recommended spellcheckers.\n"
            "☐ Run 'codespell' to run the Codespell spellchecker.\n"
            "✔ Adding recommended test frameworks.\n"
            "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
            "☐ Add test functions with the format 'test_*()'.\n"
            "☐ Run 'pytest' to run the tests.\n"
            "☐ Run 'pytest --cov' to run your tests with Coverage.py.\n"
        )
