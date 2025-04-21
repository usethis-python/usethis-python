from pathlib import Path

from usethis._integrations.ci.bitbucket.used import is_bitbucket_used
from usethis._test import change_cwd


class TestIsBitbucketUsed:
    def test_file_exists(self, tmp_path: Path):
        (tmp_path / "bitbucket-pipelines.yml").touch()
        with change_cwd(tmp_path):
            assert is_bitbucket_used()

    def test_file_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path):
            assert not is_bitbucket_used()
