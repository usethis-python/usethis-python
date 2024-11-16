from pathlib import Path

from usethis._integrations.bitbucket.config import _YAML_CONTENTS
from usethis._integrations.bitbucket.io import (
    edit_bitbucket_pipelines_yaml,
)
from usethis._test import change_cwd


class TestEditBitbucketPipelinesYAML:
    def test_do_nothing(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
"""
        )

        # Act
        with change_cwd(uv_init_dir), edit_bitbucket_pipelines_yaml() as _:
            pass

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
"""
        )

    def test_change_image(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
"""
        )

        # Act
        with change_cwd(uv_init_dir), edit_bitbucket_pipelines_yaml() as doc:
            assert isinstance(doc.content, dict)  # Help pyright
            doc.content["image"] = "atlassian/default-image:2"

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:2
"""
        )

    def test_change_default(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
pipelines:
    default:
      - step:
            script:
              - echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(uv_init_dir), edit_bitbucket_pipelines_yaml() as doc:
            # Help pyright with assertions
            assert isinstance(doc.content, dict)
            assert isinstance(doc.content["pipelines"], dict)
            assert isinstance(doc.content["pipelines"]["default"], list)
            assert isinstance(doc.content["pipelines"]["default"][0], dict)
            assert isinstance(doc.content["pipelines"]["default"][0]["step"], dict)
            doc.content["pipelines"]["default"][0]["step"]["script"] = ["echo 'Bye!'"]

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
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

    def test_roundtrip_indentation(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
pipelines:
      default:
          - step:
                  script:
                      - echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(uv_init_dir), edit_bitbucket_pipelines_yaml() as _:
            pass

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
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

    def test_default_yaml_contents_do_nothing(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(_YAML_CONTENTS)

        # Act
        with change_cwd(uv_init_dir), edit_bitbucket_pipelines_yaml() as _:
            pass

        # Assert
        assert (uv_init_dir / "bitbucket-pipelines.yml").read_text() == _YAML_CONTENTS
