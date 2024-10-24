from pathlib import Path

from usethis._integrations.bitbucket.steps import Step, add_steps
from usethis._utils._test import change_cwd


class TestAddStep:
    def test_contents(self, uv_init_dir: Path):
        # Arrange

        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
  default: []
"""
        )

        # Act
        with change_cwd(uv_init_dir):
            add_steps(
                [
                    Step(
                        name="Greeting",
                        caches=[],
                        script=["echo 'Hello, world!'"],
                    )
                ],
                is_parallel=False,
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
      name: Greeting
      script:
      - echo 'Hello, world!'
"""
        )
