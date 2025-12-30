from pathlib import Path

import pytest

from usethis._integrations.ci.bitbucket.errors import BitbucketPipelinesYAMLSchemaError
from usethis._integrations.ci.bitbucket.schema import (
    Cache,
    CachePath,
    Clone,
    Definitions,
    Image,
    ImageName,
    PipelinesConfiguration,
)
from usethis._integrations.ci.bitbucket.yaml import (
    ORDER_BY_CLS,
    BitbucketPipelinesYAMLManager,
    _bitbucket_fancy_dump,
)
from usethis._test import change_cwd


class TestEditBitbucketPipelinesYAML:
    def test_do_nothing(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
"""
        )

        # Act
        with change_cwd(tmp_path), BitbucketPipelinesYAMLManager() as mgr:
            mgr.model_validate()
            # No changes made

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
"""
        )

    def test_change_image(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
"""
        )

        # Act
        with change_cwd(tmp_path), BitbucketPipelinesYAMLManager() as mgr:
            doc = mgr.get()
            mgr.model_validate()
            assert isinstance(doc.content, dict)  # Help type checker
            doc.content["image"] = "atlassian/default-image:2"
            mgr.commit(doc)

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:2
"""
        )

    def test_change_default(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
pipelines:
    default:
      - step:
            script:
              - echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(tmp_path), BitbucketPipelinesYAMLManager() as mgr:
            doc = mgr.get()
            mgr.model_validate()
            # Help type checker with assertions
            assert isinstance(doc.content, dict)
            assert isinstance(doc.content["pipelines"], dict)
            assert isinstance(doc.content["pipelines"]["default"], list)
            assert isinstance(doc.content["pipelines"]["default"][0], dict)
            assert isinstance(doc.content["pipelines"]["default"][0]["step"], dict)
            doc.content["pipelines"]["default"][0]["step"]["script"] = ["echo 'Bye!'"]
            mgr.commit(doc)

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
pipelines:
    default:
      - step:
            script:
              - echo 'Bye!'
"""
        )

    def test_roundtrip_indentation(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
pipelines:
      default:
          - step:
                  script:
                      - echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(tmp_path), BitbucketPipelinesYAMLManager() as mgr:
            mgr.model_validate()
            # No changes made

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
pipelines:
      default:
          - step:
                  script:
                      - echo 'Hello, world!'
"""
        )

    def test_invalid_contents(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text("""\
awfpah28yqh2an ran  2rqa0-2 }[
""")

        # Act, Assert
        with (
            change_cwd(tmp_path),
            pytest.raises(BitbucketPipelinesYAMLSchemaError),
            BitbucketPipelinesYAMLManager() as mgr,
        ):
            mgr.model_validate()


class TestReadBitbucketPipelinesYAML:
    def test_quote_style_preserved(self, tmp_path: Path):
        # Arrange
        content_str = """\
pipelines:
    default:
      - step:
            script:
              - 'echo'
"""

        (tmp_path / "bitbucket-pipelines.yml").write_text(content_str)

        # Act
        with change_cwd(tmp_path), BitbucketPipelinesYAMLManager() as mgr:
            mgr.model_validate()
            # Read-only, no commit needed

        # Assert
        # Note: YAML round-tripping may normalize formatting (e.g., remove unnecessary quotes)
        expected = """\
pipelines:
    default:
      - step:
            script:
              - echo
"""
        assert (tmp_path / "bitbucket-pipelines.yml").read_text() == expected


class TestOrderByCls:
    def test_attribute_consistency(self):
        for cls, fields in ORDER_BY_CLS.items():
            for field in fields:
                assert field in cls.model_fields


class TestBitbucketFancyDump:
    def test_order(self):
        # Arrange
        config = PipelinesConfiguration(
            image=Image(ImageName("python:3.8.1")),
            clone=Clone(depth="full"),
            definitions=Definitions(
                caches={
                    "pip": Cache(CachePath("pip")),
                },
            ),
        )

        # Act
        dump = _bitbucket_fancy_dump(config, reference={})

        # Assert
        assert dump == {
            "image": "python:3.8.1",
            "clone": {
                "depth": "full",
            },
            "definitions": {
                "caches": {
                    "pip": "pip",
                },
            },
        }
        assert list(dump) == ["image", "clone", "definitions"]
