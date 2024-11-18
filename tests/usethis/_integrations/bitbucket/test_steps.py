from pathlib import Path

from usethis._integrations.bitbucket.pipeline import (
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
    add_step_in_default,
    anchorize_script_refs,
    get_steps_in_pipeline_item,
)
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


class TestAnchorizeScriptRefs:
    def test_no_lookup(self):
        # Arrange
        step = Step(
            name="Greeting",
            script=Script(["echo 'Hello, world!'"]),
        )

        # Act
        new_step = anchorize_script_refs(step, script_item_by_name={})

        # Assert
        assert new_step == step

    def test_lookup(self):
        # Arrange
        step = Step(name="Greeting", script=Script(["usethis-anchor-example"]))

        # Act
        new_step = anchorize_script_refs(step, script_item_by_name={"example": "value"})

        # Assert
        assert new_step == Step(name="Greeting", script=Script(["value"]))
        # Check no mutation/side-effects on the original
        assert step == Step(name="Greeting", script=Script(["usethis-anchor-example"]))

    def test_unknown_lookup(self):
        # Arrange
        step = Step(name="Greeting", script=Script(["usethis-anchor-example"]))

        # Act
        new_step = anchorize_script_refs(step, script_item_by_name={})

        # Assert
        assert new_step == Step(
            name="Greeting", script=Script(["usethis-anchor-example"])
        )

    def test_unused_lookup(self):
        # Arrange
        step = Step(name="Greeting", script=Script(["script"]))

        # Act
        new_step = anchorize_script_refs(
            step, script_item_by_name={"example2": "value"}
        )

        # Assert
        assert new_step == Step(name="Greeting", script=Script(["script"]))


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
