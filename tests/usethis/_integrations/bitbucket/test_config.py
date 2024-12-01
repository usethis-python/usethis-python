from pathlib import Path

from usethis._integrations.bitbucket.config import (
    _YAML_CONTENTS,
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._integrations.bitbucket.schema import Model, Script
from usethis._integrations.bitbucket.steps import (
    _ANCHOR_PREFIX,
    Step,
    add_step_in_default,
)
from usethis._integrations.yaml.io import edit_yaml
from usethis._test import change_cwd


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

    def test_satisfies_schema(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            add_bitbucket_pipeline_config()
            add_step_in_default(
                Step(
                    name="Placeholder - add your own steps!",
                    script=Script(
                        [f"{_ANCHOR_PREFIX}-install-uv", "echo 'Hello, world!'"]
                    ),
                ),
            )

        # Assert
        with edit_yaml(tmp_path / "bitbucket-pipelines.yml") as yaml_document:
            assert Model.model_validate(yaml_document.content)


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
