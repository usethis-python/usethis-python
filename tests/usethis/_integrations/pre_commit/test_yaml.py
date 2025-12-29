from pathlib import Path
from typing import cast

import pytest

from usethis._config_file import files_manager
from usethis._integrations.pre_commit.errors import PreCommitConfigYAMLConfigError
from usethis._integrations.pre_commit.hooks import _get_placeholder_repo_config
from usethis._integrations.pre_commit.schema import (
    JsonSchemaForPreCommitConfigYaml,
)
from usethis._integrations.pre_commit.yaml import (
    PreCommitConfigYAMLManager,
    _pre_commit_fancy_dump,
)
from usethis._test import change_cwd


class TestEditPreCommitConfigYAML:
    def test_unchanged(self, tmp_path: Path):
        # Arrange
        content_str = """\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
        additional_dependencies: ['validate-pyproject-schema-store[all]']
"""
        (tmp_path / ".pre-commit-config.yaml").write_text(content_str)

        # Act
        with change_cwd(tmp_path), PreCommitConfigYAMLManager() as mgr:
            mgr.model_validate()
            # No changes made

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == content_str

    def test_start_with_empty_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("")

        # Act
        with change_cwd(tmp_path), files_manager():
            mgr = PreCommitConfigYAMLManager()
            doc = mgr.get()
            mgr.model_validate()
            content = cast("dict", doc.content)
            content["repos"] = []
            mgr.commit(doc)

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == "repos: []\n"

    def test_extra_config(self, tmp_path: Path):
        # Arrange
        content_str = """\
repos:
    - repo: https://github.com/abravalheri/validate-pyproject
      rev: v0.23
extra:
    - something
"""

        (tmp_path / ".pre-commit-config.yaml").write_text(content_str)

        # Act / Assert
        with change_cwd(tmp_path), PreCommitConfigYAMLManager() as mgr:
            mgr.model_validate()
            # No changes made

        assert (tmp_path / ".pre-commit-config.yaml").read_text() == content_str


class TestReadPreCommitConfigYAML:
    def test_quote_style_preserved(self, tmp_path: Path):
        # Arrange
        content_str = """\
repos:
    - repo: 'https://github.com/abravalheri/validate-pyproject'
      rev: 'v0.23'
"""

        (tmp_path / ".pre-commit-config.yaml").write_text(content_str)

        # Act
        with change_cwd(tmp_path), PreCommitConfigYAMLManager():
            # Just reading, no modifications
            pass

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == content_str

    def test_invalid_config_raises(self, tmp_path: Path):
        # Arrange
        content_str = """\
repos:
    - invalid_entry
"""

        (tmp_path / ".pre-commit-config.yaml").write_text(content_str)

        # Act / Assert
        with (
            change_cwd(tmp_path),
            pytest.raises(
                PreCommitConfigYAMLConfigError,
                match=r"Invalid '.pre-commit-config.yaml' file:",
            ),
            PreCommitConfigYAMLManager() as mgr,
        ):
            mgr.model_validate()

    def test_extra_config(self, tmp_path: Path):
        # Arrange
        content_str = """\
repos:
    - repo: https://github.com/abravalheri/validate-pyproject
      rev: v0.23
extra:
    - something
"""

        (tmp_path / ".pre-commit-config.yaml").write_text(content_str)

        # Act / Assert
        with (
            change_cwd(tmp_path),
            PreCommitConfigYAMLManager() as mgr,
        ):
            doc = mgr.get()
            mgr.model_validate()
            content = cast("dict", doc.content)
            content["repos"] = ["something"]


class TestPreCommitFancyDump:
    def test_placeholder(self, tmp_path: Path):
        # Arrange - create a minimal pre-commit config for get_system_language()
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")

        # Act
        with change_cwd(tmp_path), files_manager():
            _pre_commit_fancy_dump(
                config=JsonSchemaForPreCommitConfigYaml(
                    repos=[
                        _get_placeholder_repo_config(),
                    ]
                ),
                reference={},
            )

    def test_invalid(self):
        with pytest.raises(TypeError):
            _pre_commit_fancy_dump(
                config=2,  # type: ignore for test
                reference={},
            )
