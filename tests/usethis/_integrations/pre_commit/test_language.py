from pathlib import Path

from usethis._config_file import files_manager
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.pre_commit.schema import Language
from usethis._test import change_cwd


class TestGetSystemLanguage:
    def test_returns_unsupported_when_minimum_version_is_4_4_0(self, tmp_path: Path):
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
            result = get_system_language()

        # Assert
        assert result == Language("unsupported")

    def test_returns_unsupported_when_minimum_version_is_above_4_4_0(
        self, tmp_path: Path
    ):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_pre_commit_version: '4.5.0'
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_system_language()

        # Assert
        assert result == Language("unsupported")

    def test_returns_system_when_minimum_version_is_below_4_4_0(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_pre_commit_version: '4.3.0'
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_system_language()

        # Assert
        assert result == Language("system")

    def test_returns_system_when_config_doesnt_exist(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_system_language()

        # Assert
        assert result == Language("system")

    def test_returns_system_when_minimum_version_not_declared(self, tmp_path: Path):
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
            result = get_system_language()

        # Assert
        assert result == Language("system")

    def test_returns_system_when_minimum_version_is_3_x(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_pre_commit_version: '3.7.1'
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.23
    hooks:
      - id: validate-pyproject
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_system_language()

        # Assert
        assert result == Language("system")
