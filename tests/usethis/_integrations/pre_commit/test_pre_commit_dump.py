import pytest

from usethis._integrations.pre_commit.dump import pre_commit_fancy_dump
from usethis._integrations.pre_commit.hooks import _get_placeholder_repo_config
from usethis._integrations.pre_commit.schema import (
    JsonSchemaForPreCommitConfigYaml,
)


class TesttPreCommitFancyDump:
    def test_placeholder(self):
        pre_commit_fancy_dump(
            config=JsonSchemaForPreCommitConfigYaml(
                repos=[
                    _get_placeholder_repo_config(),
                ]
            ),
            reference={},
        )

    def test_invalid(self):
        with pytest.raises(TypeError):
            pre_commit_fancy_dump(
                config=2,  # type: ignore for test
                reference={},
            )
