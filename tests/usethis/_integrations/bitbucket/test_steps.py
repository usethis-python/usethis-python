from pathlib import Path

from usethis._integrations.bitbucket.pipeline import Script
from usethis._integrations.bitbucket.steps import Step, add_step_in_default
from usethis._test import change_cwd


class TestAddStepInDefault:
    def test_contents(self, uv_init_dir: Path):
        # Arrange

        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            script: ["echo 'Hello, world!'"]
"""
        )

        # Act
        with change_cwd(uv_init_dir):
            add_step_in_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Why, hello!'"]),
                ),
            )

        # Assert
        with open(uv_init_dir / "bitbucket-pipelines.yml") as f:
            contents = f.read()
        assert (
            contents
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            script: ["echo 'Hello, world!'"]
      - step:
            name: Greeting
            script:
              - echo 'Why, hello!'
"""
        )

    def test_pipeline_doesnt_exist(self, uv_init_dir: Path):
        # Arrange

        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines: {}
"""
        )

        # Act
        with change_cwd(uv_init_dir):
            add_step_in_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
pipelines:
  default:
  - step:
      name: Greeting
      script:
      - echo 'Hello, world!'
"""
        )

    def test_with_caches(self, uv_init_dir: Path):
        # Arrange

        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines: {}
"""
        )

        # Act
        with change_cwd(uv_init_dir):
            add_step_in_default(
                Step(
                    name="Greeting",
                    caches=["uv"],
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
definitions:
  caches:
    uv: ~/.cache/uv
pipelines:
  default:
  - step:
      name: Greeting
      caches:
      - uv
      script:
      - echo 'Hello, world!'
"""
        )
