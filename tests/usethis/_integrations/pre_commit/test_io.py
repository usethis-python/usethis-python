from pathlib import Path

from usethis._integrations.pre_commit.io import edit_pre_commit_config_yaml
from usethis._test import change_cwd


class TestEditPreCommitConfigYAML:
    def test_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path), edit_pre_commit_config_yaml():
            pass

        assert (tmp_path / ".pre-commit-config.yaml").exists()

    # TODO really should have a lot more tests here - check test coverage.
