from pathlib import Path

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.pre_commit import PreCommitTool


class TestPreCommitTool:
    class TestIsUsed:
        def test_pre_commit_config_file(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").touch()

            # Act, Assert
            with change_cwd(tmp_path):
                assert PreCommitTool().is_used()

        def test_pre_commit_disabled(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").touch()

            # Act, Assert
            with change_cwd(tmp_path), usethis_config.set(disable_pre_commit=True):
                assert not PreCommitTool().is_used()

        def test_empty_dir(self, tmp_path: Path):
            # Act, Assert
            with change_cwd(tmp_path), files_manager():
                assert not PreCommitTool().is_used()
