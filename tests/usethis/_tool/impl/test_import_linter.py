from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.import_linter import ImportLinterTool, _is_inp_rule


class TestImportLinterTool:
    class TestPrintHowToUse:
        def test_pre_commit_and_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / "uv.lock").touch()
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: import-linter
        name: import-linter
        entry: uv run --frozen --offline lint-imports
""")
            (tmp_path / "ruff.toml").write_text(  # For avoid info/hint messages
                'lint.select=["INP"]'
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'uv run pre-commit run import-linter --all-files' to run Import Linter.\n"
            )

        def test_pre_commit_no_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: import-linter
        name: import-linter
        entry: uv run --frozen --offline lint-imports
""")
            (tmp_path / "ruff.toml").write_text(  # For avoid info/hint messages
                'lint.select=["INP"]'
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'pre-commit run import-linter --all-files' to run Import Linter.\n"
            )

        def test_uv_only(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "uv.lock").touch()
            (tmp_path / "ruff.toml").write_text(  # For avoid info/hint messages
                'lint.select=["INP"]'
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'uv run lint-imports' to run Import Linter.\n")

        def test_basic(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "ruff.toml").write_text(  # For avoid info/hint messages
                'lint.select=["INP"]'
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'lint-imports' to run Import Linter.\n")

        def test_ruff_isnt_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "ℹ Ensure '__init__.py' files are used in your packages.\n"  # noqa: RUF001
                "ℹ For more info see <https://docs.python.org/3/tutorial/modules.html#packages>\n"  # noqa: RUF001
                "☐ Run 'lint-imports' to run Import Linter.\n"
            )

        def test_ruff_is_used_without_inp_rules(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # https://github.com/usethis-python/usethis-python/issues/817

            # Arrange
            (tmp_path / "ruff.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "ℹ Ensure '__init__.py' files are used in your packages.\n"  # noqa: RUF001
                "ℹ For more info see <https://docs.python.org/3/tutorial/modules.html#packages>\n"  # noqa: RUF001
                "☐ Run 'lint-imports' to run Import Linter.\n"
            )

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect .importlinter to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().add_configs()

            # Assert
            assert (tmp_path / ".importlinter").exists()
            assert not (tmp_path / "pyproject.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                ImportLinterTool().add_configs()

            # Assert
            assert not (tmp_path / ".importlinter").exists()
            assert (tmp_path / "pyproject.toml").exists()


class TestIsINPRule:
    def test_inp_rule(self):
        assert _is_inp_rule("INP001")

    def test_no_digits(self):
        assert _is_inp_rule("INP")
