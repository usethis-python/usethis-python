from pathlib import Path

import pytest
import yamltrip

from _test import change_cwd
from usethis._config_file import files_manager
from usethis._integrations.pre_commit.errors import PreCommitConfigYAMLConfigError
from usethis._integrations.pre_commit.yaml import (
    PreCommitConfigYAMLManager,
)


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
        with change_cwd(tmp_path), files_manager():
            mgr = PreCommitConfigYAMLManager()
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
            mgr.model_validate()
            mgr.set_value(keys=["repos"], value=[], exists_ok=True)

        # Assert
        content = (tmp_path / ".pre-commit-config.yaml").read_text()
        doc = yamltrip.loads(content)
        assert doc[()] == {"repos": []}

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
        with change_cwd(tmp_path), files_manager():
            mgr = PreCommitConfigYAMLManager()
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
        with change_cwd(tmp_path), files_manager():
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
            files_manager(),
        ):
            PreCommitConfigYAMLManager().model_validate()

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
            files_manager(),
        ):
            mgr = PreCommitConfigYAMLManager()
            doc = mgr.get()
            mgr.model_validate()
            content = doc.doc[()]
            assert "repos" in content
            assert "extra" in content
