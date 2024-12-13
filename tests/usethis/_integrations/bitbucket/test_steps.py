from pathlib import Path

import pytest

from usethis._integrations.bitbucket.schema import (
    Parallel,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Script,
    Stage,
    StageItem,
    Step1,
    Step2,
    StepItem,
)
from usethis._integrations.bitbucket.steps import (
    Step,
    add_placeholder_step_in_default,
    add_step_in_default,
    get_steps_in_pipeline_item,
)
from usethis._test import change_cwd


class TestAddStepInDefault:
    def test_contents(self, tmp_path: Path):
        # Arrange

        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            script: ["echo 'Hello, world!'"]
"""
        )

        # Act
        with change_cwd(tmp_path):
            add_step_in_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Why, hello!'"]),
                ),
            )

        # Assert
        with open(tmp_path / "bitbucket-pipelines.yml") as f:
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

    def test_pipeline_doesnt_exist(self, tmp_path: Path):
        # Arrange

        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines: {}
"""
        )

        # Act
        with change_cwd(tmp_path):
            add_step_in_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
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

    def test_with_caches(self, tmp_path: Path):
        # Arrange

        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines: {}
"""
        )

        # Act
        with change_cwd(tmp_path):
            add_step_in_default(
                Step(
                    name="Greeting",
                    caches=["uv"],
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
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


class TestGetStepsInPipelineItem:
    class TestStepItem:
        def test_none(self):
            # Arrange
            item = StepItem(step=None)

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == []

        def test_step(self):
            # Arrange
            step = Step(script=Script(["echo 'Hello, world!'"]))
            item = StepItem(step=step)

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == [step]

    class TestParallelItem:
        def test_none(self):
            # Arrange
            item = ParallelItem(parallel=None)

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == []

        def test_parallel_steps(self):
            # Arrange
            original_steps = [
                Step(script=Script(["echo 'Hello, world!'"])),
                Step(script=Script(["echo 'Why, hello!'"])),
            ]
            item = ParallelItem(
                parallel=Parallel(
                    ParallelSteps([StepItem(step=step) for step in original_steps])
                )
            )

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == original_steps

        def test_parallel_expanded(self):
            # Arrange
            original_steps = [
                Step(script=Script(["echo 'Hello, world!'"])),
                Step(script=Script(["echo 'Why, hello!'"])),
            ]
            item = ParallelItem(
                parallel=Parallel(
                    ParallelExpanded(
                        steps=ParallelSteps(
                            [StepItem(step=step) for step in original_steps]
                        )
                    )
                )
            )

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == original_steps

    class TestStageItem:
        def test_none(self):
            # Arrange
            item = StageItem(stage=None)

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == []

        def test_steps(self):
            # Arrange
            script = Script(["echo 'Hello, world!'"])
            item = StageItem(
                stage=Stage(
                    steps=[
                        Step1(step=None),
                        Step1(
                            step=Step2(
                                name="greetings",
                                script=Script(["echo 'Hello, world!'"]),
                            )
                        ),
                    ]
                )
            )

            # Act
            steps = get_steps_in_pipeline_item(item)

            # Assert
            assert steps == [Step(name="greetings", script=script)]


class TestAddPlaceholderStepInDefault:
    def test_contents(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # TODO do the same for pre-commit
        # Act
        with change_cwd(tmp_path):
            add_placeholder_step_in_default()

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        assert (
            (tmp_path / "bitbucket-pipelines.yml").read_text()
            == """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
    script_items:
      - &install-uv |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.local/bin/env
        export UV_LINK_MODE=copy
        uv --version
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            caches:
              - uv
            script:
              - *install-uv
              - echo 'Hello, world!'
"""
        )

        out, _ = capfd.readouterr()
        assert out == (
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding placeholder step in default pipeline in 'bitbucket-pipelines.yml'.\n"
            "☐ Replace placeholder pipeline step in 'bitbucket-pipelines.yml'.\n"
        )
