from pathlib import Path

from usethis._integrations.pre_commit.io_ import edit_pre_commit_config_yaml
from usethis._test import change_cwd


class TestEditPreCommitConfigYAML:
    def test_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path), edit_pre_commit_config_yaml():
            pass

        assert (tmp_path / ".pre-commit-config.yaml").exists()

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
        with change_cwd(tmp_path), edit_pre_commit_config_yaml() as _:
            pass

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == content_str

    def test_start_with_empty_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("")

        # Act
        with (
            change_cwd(tmp_path),
            edit_pre_commit_config_yaml() as doc,
        ):
            doc.content["repos"] = []

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == "repos: []\n"

    def test_empty_valid_but_unchanged(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("")

        # Act
        with change_cwd(tmp_path), edit_pre_commit_config_yaml():
            pass

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == ""
