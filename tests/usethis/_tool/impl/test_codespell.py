import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit import schema
from usethis._python.version import PythonVersion
from usethis._test import change_cwd
from usethis._tool.impl.codespell import CodespellTool
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency


class TestCodespellTool:
    class TestDefaultCommand:
        def test_uv_backend_with_uv_lock(self, tmp_path: Path):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = CodespellTool().default_command()

            # Assert
            assert cmd == "uv run codespell"

        def test_uv_backend_without_uv_lock(self, tmp_path: Path):
            # Arrange - no uv.lock file

            # Act
            with change_cwd(tmp_path), files_manager():
                cmd = CodespellTool().default_command()

            # Assert
            assert cmd == "codespell"

        def test_none_backend(self, tmp_path: Path):
            # Arrange

            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                cmd = CodespellTool().default_command()

            # Assert
            assert cmd == "codespell"

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
        assert isinstance(repo, schema.UriRepo)
        try:
            assert repo.rev == get_github_latest_tag(
                owner="codespell-project", repo="codespell"
            )
        except GitHubTagError as err:
            if (
                usethis_config.offline
                or "rate limit exceeded for url" in str(err)
                or "Read timed out." in str(err)
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

    class TestGetDevDeps:
        def test_requires_python_includes_3_10(self, tmp_path: Path):
            # Arrange
            # Create a pyproject.toml with requires-python that includes Python 3.10
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.10"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps()

            # Assert
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") in deps

        def test_requires_python_only_3_11_and_above(self, tmp_path: Path):
            # Arrange
            # Create a pyproject.toml with requires-python that only includes Python >= 3.11
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.11"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps()

            # Assert
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") not in deps

        def test_requires_python_range_includes_3_10(self, tmp_path: Path):
            # Arrange
            # Create a pyproject.toml with requires-python range that includes 3.10
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.10,<3.13"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps()

            # Assert
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") in deps

        def test_no_pyproject_toml_3pt10(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Arrange - no pyproject.toml file, using interpreter version
            monkeypatch.setattr(
                "usethis._python.version.PythonVersion.from_interpreter",
                lambda: PythonVersion(major="3", minor="10", patch=None),
            )
            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps()

            # Assert
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") in deps

        def test_no_pyproject_toml_3pt11(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Arrange - no pyproject.toml file, using interpreter version
            monkeypatch.setattr(
                "usethis._python.version.PythonVersion.from_interpreter",
                lambda: PythonVersion(major="3", minor="11", patch=None),
            )
            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps()

            # Assert
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") not in deps

        def test_unconditional_includes_tomli(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.12"
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                deps = CodespellTool().get_dev_deps(unconditional=True)

            # Assert
            # When unconditional=True, tomli should always be included
            assert Dependency(name="codespell") in deps
            assert Dependency(name="tomli") in deps
