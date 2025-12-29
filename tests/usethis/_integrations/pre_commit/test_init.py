from pathlib import Path

from usethis._integrations.pre_commit.init import ensure_pre_commit_config_exists
from usethis._test import change_cwd


class TestEnsurePreCommitConfigExists:
    def test_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path):
            ensure_pre_commit_config_exists()

        assert (tmp_path / ".pre-commit-config.yaml").exists()

    def test_empty_valid_but_unchanged(self, tmp_path: Path):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("")

        # Act
        with change_cwd(tmp_path):
            ensure_pre_commit_config_exists()
            # File exists, so it is not modified even if empty

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == ""
