from pathlib import Path

from typer.testing import CliRunner

from usethis._app import app
from usethis._integrations.pre_commit.hooks import get_hook_ids
from usethis._test import change_cwd


class TestInit:
    def test_pre_commit_included(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["init", "--pre-commit"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "✔ Writing 'pyproject.toml' and initializing project.\n"
            "✔ Adding the pre-commit framework.\n"
            "☐ Run 'uv run pre-commit run --all-files' to run the hooks manually.\n"
            "✔ Adding recommended linters.\n"
            "☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'uv run deptry src' to run deptry.\n"
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
        )

        # Check the pre-commit hooks are added in the correct order
        with change_cwd(tmp_path):
            hook_ids = get_hook_ids()
            assert hook_ids == [
                "pyproject-fmt",
                "ruff",
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
            result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            # ###################################
            # See docstring!
            # ###################################
            == """\
✔ Writing 'pyproject.toml' and initializing project.
✔ Adding recommended linters.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run deptry src' to run deptry.
✔ Adding recommended formatters.
☐ Run 'uv run ruff format' to run the Ruff formatter.
☐ Run 'uv run pyproject-fmt pyproject.toml' to run pyproject-fmt.
✔ Adding recommended spellcheckers.
☐ Run 'uv run codespell' to run the Codespell spellchecker.
✔ Adding recommended test frameworks.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
"""
        )

    def test_specify_path(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["init", "myproject"])

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
            result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_bitbucket_and_docstyle(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(
                app,
                ["init", "--ci", "bitbucket", "--docstyle", "numpy", "--pre-commit"],
            )

        # Assert
        assert result.exit_code == 0, result.output
        assert (tmp_path / "pyproject.toml").exists()
        assert result.output == (
            "✔ Writing 'pyproject.toml' and initializing project.\n"
            "✔ Adding the pre-commit framework.\n"
            "☐ Run 'uv run pre-commit run --all-files' to run the hooks manually.\n"
            "✔ Adding recommended linters.\n"
            "☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.\n"
            "☐ Run 'uv run deptry src' to run deptry.\n"
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
            "✔ Adding Bitbucket Pipelines configuration.\n"
            "☐ Run your pipeline via the Bitbucket website.\n"
        )
