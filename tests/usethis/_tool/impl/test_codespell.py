import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit.schema import UriRepo
from usethis._test import change_cwd
from usethis._tool.impl.codespell import CodespellTool


class TestCodespellTool:
    class TestPrintHowToUse:
        def test_pre_commit_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # https://github.com/usethis-python/usethis-python/issues/802

            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text(
                """\
repos:
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.1
    hooks:
      - id: codespell
        additional_dependencies:
          - tomli
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                CodespellTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'pre-commit run codespell --all-files' to run the Codespell spellchecker.\n"
            )

        def test_pre_commit_used_but_not_configured(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # https://github.com/usethis-python/usethis-python/issues/802

            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.codespell]
"""
            )
            (tmp_path / ".pre-commit-config.yaml").write_text(
                """\
repos: []
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                CodespellTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'codespell' to run the Codespell spellchecker.\n")

        def test_both_devdep_and_pre_commit_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[dependency-groups]
dev = ["codespell"]
"""
            )
            (tmp_path / ".pre-commit-config.yaml").write_text(
                """\
repos:
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.1
    hooks:
      - id: codespell
        additional_dependencies:
          - tomli
"""
            )
            # Act
            with change_cwd(tmp_path), files_manager():
                CodespellTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("☐ Run 'codespell' to run the Codespell spellchecker.\n")

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        (config,) = CodespellTool().get_pre_commit_config().repo_configs
        repo = config.repo
        assert isinstance(repo, UriRepo)
        try:
            assert repo.rev == get_github_latest_tag(
                owner="codespell-project", repo="codespell"
            )
        except GitHubTagError as err:
            if (
                os.getenv("CI")
                or usethis_config.offline
                or "rate limit exceeded for url" in str(err)
            ):
                pytest.skip(
                    "Failed to fetch GitHub tags (connection issues); skipping test"
                )
            raise err

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect ruff.toml to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                CodespellTool().add_configs()

            # Assert
            assert (tmp_path / ".codespellrc").exists()
            assert not (tmp_path / "setup.cfg").exists()
            assert not (tmp_path / "pyproject.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                CodespellTool().add_configs()

            # Assert
            assert not (tmp_path / ".codespellrc").exists()
            assert not (tmp_path / "setup.cfg").exists()
            assert (tmp_path / "pyproject.toml").exists()
