from pathlib import Path

from usethis._config_file import files_manager
from usethis._integrations.pre_commit.version import (
    PRE_COMMIT_VERSION,
    get_minimum_pre_commit_version,
    get_pre_commit_version,
)
from usethis._test import change_cwd


class TestGetMinimumPreCommitVersion:
    def test_happy_path(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_pre_commit_version: '4.4.0'
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_minimum_pre_commit_version()

        # Assert
        assert result == "4.4.0"

    def test_config_doesnt_exist(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = get_minimum_pre_commit_version()

        # Assert
        assert result is None

    def test_minimum_version_not_declared(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_minimum_pre_commit_version()

        # Assert
        assert result is None


class TestGetPreCommitVersion:
    def test_uses_declared_minimum_version(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_pre_commit_version: '3.5.0'
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_pre_commit_version()

        # Assert
        assert result == "3.5.0"

    def test_falls_back_to_hardcoded_when_config_doesnt_exist(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = get_pre_commit_version()

        # Assert
        assert result == PRE_COMMIT_VERSION

    def test_falls_back_to_hardcoded_when_minimum_not_declared(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_pre_commit_version()

        # Assert
        assert result == PRE_COMMIT_VERSION
