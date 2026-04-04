from pathlib import Path
from unittest.mock import patch

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._fallback import FALLBACK_UV_VERSION
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._test import change_cwd
from usethis._tool.impl.base.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.spec.requirements_txt import RequirementsTxtToolSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum

_UV_PRE_COMMIT_REPO = "https://github.com/astral-sh/uv-pre-commit"


class TestRequirementsTxtToolSpec:
    class TestMeta:
        def test_managed_files_default(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
                meta = RequirementsTxtToolSpec().meta

            assert meta.managed_files == [Path("requirements.txt")]

        def test_managed_files_custom(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
                meta = RequirementsTxtToolSpec(output_file="constraints.txt").meta

            assert meta.managed_files == [Path("constraints.txt")]

    class TestPreCommitConfig:
        def test_uv_backend_default_output_file(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.uv):
                config = RequirementsTxtToolSpec().pre_commit_config()

            assert len(config.repo_configs) == 1
            repo = config.repo_configs[0].repo
            assert isinstance(repo, pre_commit_schema.UriRepo)
            assert repo.repo == _UV_PRE_COMMIT_REPO
            assert repo.hooks is not None
            assert len(repo.hooks) == 1
            hook = repo.hooks[0]
            assert hook.id == "uv-export"
            assert hook.args is None

        def test_uv_backend_custom_output_file(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.uv):
                config = RequirementsTxtToolSpec(
                    output_file="constraints.txt"
                ).pre_commit_config()

            assert len(config.repo_configs) == 1
            repo = config.repo_configs[0].repo
            assert isinstance(repo, pre_commit_schema.UriRepo)
            hook = repo.hooks[0]  # type: ignore[index]
            assert hook.id == "uv-export"
            assert hook.args == ["--output-file=constraints.txt"]

        def test_non_uv_backend_returns_empty(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
                config = RequirementsTxtToolSpec().pre_commit_config()

            assert config == PreCommitConfig(
                repo_configs=[], inform_how_to_use_on_migrate=False
            )

        def test_poetry_backend_returns_empty(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.poetry):
                config = RequirementsTxtToolSpec().pre_commit_config()

            assert config == PreCommitConfig(
                repo_configs=[], inform_how_to_use_on_migrate=False
            )

    class TestConfigSpec:
        def test_uv_backend_has_sync_with_uv_entry(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.uv):
                spec = RequirementsTxtToolSpec().config_spec()

            assert spec.config_items != []

        def test_non_uv_backend_is_empty(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.none):
                spec = RequirementsTxtToolSpec().config_spec()

            assert spec.config_items == []

        def test_poetry_backend_is_empty(self, tmp_path: Path):
            with change_cwd(tmp_path), usethis_config.set(backend=BackendEnum.poetry):
                spec = RequirementsTxtToolSpec().config_spec()

            assert spec.config_items == []


class TestRequirementsTxtTool:
    class TestPrintHowToUse:
        def test_pre_commit_uv_backend(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange - .pre-commit-config.yaml has the uv-export hook
            (tmp_path / ".pre-commit-config.yaml").write_text(
                f"""\
repos:
  - repo: {_UV_PRE_COMMIT_REPO}
    rev: {FALLBACK_UV_VERSION}
    hooks:
      - id: uv-export
"""
            )

            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.uv),
            ):
                RequirementsTxtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'uv run pre-commit run -a uv-export' to write 'requirements.txt'.\n"
            )

        def test_pre_commit_non_uv_backend(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Exercise the elif backend in (poetry, none) branch when
            # install_method == "pre-commit" by mocking get_install_method.
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
                patch.object(
                    RequirementsTxtTool, "get_install_method", return_value="pre-commit"
                ),
            ):
                RequirementsTxtTool().print_how_to_use()

            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'pre-commit run -a uv-export' to write 'requirements.txt'.\n"
            )

        def test_pre_commit_and_not_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: uv-export
        name: uv-export
        entry: uv export --frozen --offline --quiet -o=requirements.txt
        language: system
        pass_filenames: false
        require_serial: true
""")

            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                RequirementsTxtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'usethis tool requirements.txt' to write 'requirements.txt'.\n"
            )

        def test_uv_backend_no_pre_commit(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.uv),
            ):
                RequirementsTxtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "☐ Run 'uv export -o=requirements.txt' to write 'requirements.txt'.\n"
            )

        def test_poetry_backend_no_pre_commit(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.poetry),
            ):
                RequirementsTxtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'usethis tool requirements.txt' to write 'requirements.txt'.\n"
            )

        def test_custom_output_file_non_uv_backend(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                RequirementsTxtTool(output_file="constraints.txt").print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'usethis tool requirements.txt --output-file=constraints.txt'"
                " to write 'constraints.txt'.\n"
            )

        def test_custom_output_file_already_exists_non_uv_backend(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange - file already exists, so no instruction should be printed
            (tmp_path / "constraints.txt").touch()

            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.none),
            ):
                RequirementsTxtTool(output_file="constraints.txt").print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ""
