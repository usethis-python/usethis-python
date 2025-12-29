from pathlib import Path

import pytest

from usethis._integrations.ci.bitbucket.init import (
    ensure_bitbucket_pipelines_config_exists,
)
from usethis._test import change_cwd


class TestEnsureBitbucketPipelinesConfigExists:
    def test_does_not_exist(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            ensure_bitbucket_pipelines_config_exists()

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").is_file()
        assert (
            tmp_path / "bitbucket-pipelines.yml"
        ).read_text() == "image: atlassian/default-image:3\n"
        out, err = capfd.readouterr()
        assert not err
        assert out == ("✔ Writing 'bitbucket-pipelines.yml'.\n")
