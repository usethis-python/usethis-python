from pathlib import Path

from usethis._integrations.bitbucket.config import (
    _YAML_CONTENTS,
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._utils._test import change_cwd


class TestAddBitbucketPipelineConfig:
    def test_blank_slate(self, tmp_path: Path):
        with change_cwd(tmp_path):
            add_bitbucket_pipeline_config()

        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert content == _YAML_CONTENTS

    def test_existing_file(self, tmp_path: Path):
        (tmp_path / "bitbucket-pipelines.yml").write_text("existing content")

        with change_cwd(tmp_path):
            add_bitbucket_pipeline_config()

        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert content == "existing content"


class TestRemoveBitbucketPipelineConfig:
    def test_blank_slate(self, tmp_path: Path):
        with change_cwd(tmp_path):
            remove_bitbucket_pipeline_config()

        assert not (tmp_path / "bitbucket-pipelines.yml").exists()

    def test_existing_file(self, tmp_path: Path):
        (tmp_path / "bitbucket-pipelines.yml").touch()

        with change_cwd(tmp_path):
            remove_bitbucket_pipeline_config()

        assert not (tmp_path / "bitbucket-pipelines.yml").exists()
