from pathlib import Path
from uuid import UUID

import pytest

from usethis._config_file import files_manager
from usethis._integrations.ci.bitbucket.errors import UnexpectedImportPipelineError
from usethis._integrations.ci.bitbucket.pipeweld import (
    apply_pipeweld_instruction,
    get_pipeweld_pipeline_from_default,
    get_pipeweld_step,
)
from usethis._integrations.ci.bitbucket.schema import (
    Image,
    ImageName,
    ImportPipeline,
    Items,
    Parallel,
    ParallelExpanded,
    ParallelItem,
    ParallelSteps,
    Pipeline,
    Pipelines,
    PipelinesConfiguration,
    Script,
    Stage,
    StageItem,
    Step,
    Step1,
    Step2,
    StepItem,
)
from usethis._pipeweld.containers import DepGroup, depgroup, parallel, series
from usethis._pipeweld.func import _get_instructions_for_insertion
from usethis._pipeweld.ops import InsertParallel, InsertSuccessor
from usethis._test import change_cwd


class TestApplyPipeweldInstruction:
    def test_add_to_brand_new_pipeline(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                step_to_insert=Step(name="foo", script=Script(["echo foo"])),
            )

        # Assert
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            content
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: foo
            script:
              - echo foo
"""
        )

    def test_import_pipeline_fails(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
        import: shared-pipeline:master:share-pipeline-1
"""
        )

        # Act, Assert
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(UnexpectedImportPipelineError),
        ):
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                step_to_insert=Step(name="foo", script=Script(["echo foo"])),
            )

    def test_existing_pipeline(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: bar
            script:
              - echo bar
"""
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                step_to_insert=Step(name="foo", script=Script(["echo foo"])),
            )

        # Assert
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            content
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: foo
            script:
              - echo foo
      - step:
            name: bar
            script:
              - echo bar
"""
        )

    class TestInsertAfter:
        def test_step_item(self, tmp_path: Path):
            # Arrange
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: bar
            script:
              - echo bar
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="bar"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: bar
            script:
              - echo bar
      - step:
            name: foo
            script:
              - echo foo
"""
            )

        def test_parallel_item(self, tmp_path: Path):
            # Arrange
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
              name: baz
              script:
                - echo baz
          - step:
              name: qux
              script:
                - echo qux
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="qux"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: baz
                script:
                  - echo baz
          - step:
                name: qux
                script:
                  - echo qux
      - step:
            name: foo
            script:
              - echo foo
"""
            )

        def test_parallel_expanded(self, tmp_path: Path):
            # Arrange
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          steps:
            - step:
                name: baz
                script:
                  - echo baz
            - step:
                name: qux
                script:
                  - echo qux
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="qux"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            steps:
              - step:
                    name: baz
                    script:
                      - echo baz
              - step:
                    name: qux
                    script:
                      - echo qux
      - step:
            name: foo
            script:
              - echo foo
"""
            )

        def test_stage_item(self, tmp_path: Path):
            # Arrange
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - stage:
            steps:
              - step:
                    name: baz
                    script:
                      - echo baz
"""
            )

            # Act
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="baz"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - stage:
            steps:
              - step:
                    name: baz
                    script:
                      - echo baz
      - step:
            name: foo
            script:
              - echo foo
"""
            )

    class TestInsertParallel:
        def test_simple_step(self, tmp_path: Path):
            # Arrange: Pipeline with a single step
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: bar
            script:
              - echo bar
"""
            )

            # Act: Insert foo in parallel to bar
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertParallel(step="foo", after="bar"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert: Should create a parallel block with both steps
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: bar
                script:
                  - echo bar
          - step:
                name: foo
                script:
                  - echo foo
"""
            )

        def test_add_to_existing_parallel(self, tmp_path: Path):
            # Arrange: Pipeline with an existing parallel block
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: bar
                script:
                  - echo bar
          - step:
                name: baz
                script:
                  - echo baz
"""
            )

            # Act: Insert foo in parallel to bar (which is already in a parallel block)
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertParallel(step="foo", after="bar"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert: Should add to the existing parallel block
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: bar
                script:
                  - echo bar
          - step:
                name: baz
                script:
                  - echo baz
          - step:
                name: foo
                script:
                  - echo foo
"""
            )

        def test_parallel_after_none(self, tmp_path: Path):
            # Arrange: Empty pipeline
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
"""
            )

            # Act: Insert foo in parallel at the beginning (after=None)
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertParallel(step="foo", after=None),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert: Should just add the step (parallel with no other steps is just a step)
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: foo
            script:
              - echo foo
"""
            )

        def test_add_to_existing_parallel_expanded_format(self, tmp_path: Path):
            # Arrange: Pipeline with an existing parallel block using expanded format
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            steps:
              - step:
                    name: bar
                    script:
                      - echo bar
              - step:
                    name: baz
                    script:
                      - echo baz
"""
            )

            # Act: Insert foo in parallel to bar (expanded format)
            with change_cwd(tmp_path), files_manager():
                apply_pipeweld_instruction(
                    InsertParallel(step="foo", after="bar"),
                    step_to_insert=Step(name="foo", script=Script(["echo foo"])),
                )

            # Assert: Should add to the existing parallel block
            content = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert (
                content
                == """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            steps:
              - step:
                    name: bar
                    script:
                      - echo bar
              - step:
                    name: baz
                    script:
                      - echo baz
              - step:
                    name: foo
                    script:
                      - echo foo
"""
            )


class TestBreakUpParallelism:
    """Test breaking up an existing parallel block to satisfy dependencies."""

    def test_full_parallel_breakup_sequence(self, tmp_path: Path):
        # Arrange: Start with parallel(A, B), want to insert C after A
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: A
                script:
                  - echo A
          - step:
                name: B
                script:
                  - echo B
"""
        )

        with change_cwd(tmp_path), files_manager():
            # Simulate pipeweld instructions for: series("A", "C", "B")
            # Note: step_to_insert is always C (the actual new step being added)
            # but instruction.step varies (A, B, or C) to indicate which step
            # the instruction is about (existing or new)

            # Step 1: Move A to beginning
            apply_pipeweld_instruction(
                InsertSuccessor(step="A", after=None),
                step_to_insert=Step(name="C", script=Script(["echo C"])),
            )

            # Step 2: Move B after A
            apply_pipeweld_instruction(
                InsertSuccessor(step="B", after="A"),
                step_to_insert=Step(name="C", script=Script(["echo C"])),
            )

            # Step 3: Insert C after A (C will go between A and B)
            apply_pipeweld_instruction(
                InsertSuccessor(step="C", after="A"),
                step_to_insert=Step(name="C", script=Script(["echo C"])),
            )

        # Assert: Should result in A, then C, then B in series
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            content
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: A
            script:
              - echo A
      - step:
            name: C
            script:
              - echo C
      - step:
            name: B
            script:
              - echo B
"""
        )

    def test_extract_last_step_from_parallel(self, tmp_path: Path):
        # Arrange: Parallel block with a single step
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
          - step:
                name: A
                script:
                  - echo A
      - step:
            name: B
            script:
              - echo B
"""
        )

        # Act: Extract the only step from the parallel block
        with change_cwd(tmp_path), files_manager():
            apply_pipeweld_instruction(
                InsertSuccessor(step="A", after=None),
                step_to_insert=Step(name="C", script=Script(["echo C"])),
            )

        # Assert: Parallel block should be removed entirely, leaving A and B
        content = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            content
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: A
            script:
              - echo A
      - step:
            name: B
            script:
              - echo B
"""
        )


class TestGetInstructionsForInsertion:
    class TestStr:
        def test_after_str(self):
            # Arrange
            component = "foo"
            after = "bar"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [InsertSuccessor(step="foo", after="bar")]
            assert endpoint == "foo"

        def test_after_none(self):
            # Arrange
            component = "foo"
            after = None

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [InsertSuccessor(step="foo", after=None)]
            assert endpoint == "foo"

    class TestSeries:
        def test_empty(self):
            # Arrange
            component = series()
            after = None

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == []
            assert endpoint is None

        def test_single(self):
            # Arrange
            component = series("A")
            after = "0"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [InsertSuccessor(step="A", after="0")]
            assert endpoint == "A"

        def test_multiple(self):
            # Arrange
            component = series("A", "B", "C")
            after = "0"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [
                InsertSuccessor(step="A", after="0"),
                InsertSuccessor(step="B", after="A"),
                InsertSuccessor(step="C", after="B"),
            ]
            assert endpoint == "C"

    class TestParallel:
        def test_empty(self):
            # Arrange
            component = parallel()
            after = None

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == []
            assert endpoint is None

        def test_single(self):
            # Arrange
            component = parallel("A")
            after = "0"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [InsertSuccessor(step="A", after="0")]
            assert endpoint == "A"

        def test_multiple(self):
            # Arrange
            component = parallel("A", "B", "C")
            after = "0"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [
                InsertSuccessor(step="A", after="0"),
                InsertParallel(step="B", after="0"),
                InsertParallel(step="C", after="0"),
            ]
            assert endpoint == "A"  # Alphabetical order wins tiebreaks

    class TestDepGroup:
        def test_basic(self):
            # Arrange
            component = depgroup("A", series("B", "C"), config_group="x")
            after = "0"

            # Act
            instructions, endpoint = _get_instructions_for_insertion(
                component, after=after
            )

            # Assert
            assert instructions == [
                InsertSuccessor(step="A", after="0"),
                InsertSuccessor(step="B", after="A"),
                InsertSuccessor(step="C", after="B"),
            ]

            assert endpoint == "C"


class TestGetPipeweldPipelineFromDefault:
    def test_image_only(self):
        # Arrange
        model = PipelinesConfiguration(
            image=Image(ImageName("atlassian/default-image:3"))
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        assert result == series()

    def test_import_pipeline_raises(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    ImportPipeline(
                        # import is a keyword so we need to use a dict
                        **{"import": "shared-pipeline:master:share-pipeline-1"}
                    )
                ),
            ),
        )

        # Act, Assert
        with pytest.raises(UnexpectedImportPipelineError):
            get_pipeweld_pipeline_from_default(model)

    def test_series(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    Items(
                        [
                            StepItem(
                                step=Step(
                                    name="foo",
                                    script=Script(["echo foo"]),
                                )
                            )
                        ]
                    )
                ),
            ),
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        assert result == series("foo")

    def test_parallel(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    Items(
                        [
                            ParallelItem(
                                parallel=Parallel(
                                    ParallelSteps(
                                        [
                                            StepItem(
                                                step=Step(
                                                    name="foo",
                                                    script=Script(["echo foo"]),
                                                )
                                            ),
                                            StepItem(
                                                step=Step(
                                                    name="bar",
                                                    script=Script(["echo bar"]),
                                                )
                                            ),
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                ),
            ),
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        assert result == series(
            parallel("foo", "bar"),
        )

    def test_parallel_expanded(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    Items(
                        [
                            ParallelItem(
                                parallel=Parallel(
                                    ParallelExpanded(
                                        steps=ParallelSteps(
                                            [
                                                StepItem(
                                                    step=Step(
                                                        name="foo",
                                                        script=Script(["echo foo"]),
                                                    )
                                                ),
                                                StepItem(
                                                    step=Step(
                                                        name="bar",
                                                        script=Script(["echo bar"]),
                                                    )
                                                ),
                                            ]
                                        )
                                    )
                                )
                            )
                        ]
                    )
                ),
            ),
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        assert result == series(
            parallel("foo", "bar"),
        )

    def test_named_stage_item(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    Items(
                        [
                            StageItem(
                                stage=Stage(
                                    name="mystage",
                                    steps=[
                                        Step1(
                                            step=Step2(
                                                name="foo",
                                                script=Script(["echo foo"]),
                                            )
                                        )
                                    ],
                                )
                            )
                        ]
                    )
                ),
            ),
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        assert result == series(
            depgroup(
                "foo",
                config_group="mystage",
            )
        )

    def test_unnamed_stage_item(self):
        # Arrange
        model = PipelinesConfiguration(
            pipelines=Pipelines(
                default=Pipeline(
                    Items(
                        [
                            StageItem(
                                stage=Stage(
                                    steps=[
                                        Step1(
                                            step=Step2(
                                                name="foo",
                                                script=Script(["echo foo"]),
                                            )
                                        )
                                    ],
                                )
                            )
                        ]
                    )
                ),
            ),
        )

        # Act
        result = get_pipeweld_pipeline_from_default(model)

        # Assert
        dg = result[0]
        assert isinstance(dg, DepGroup)
        assert result == series(
            depgroup(
                "foo",
                config_group=dg.config_group,
            )
        )
        assert dg.config_group.startswith("Unnamed Stage ")
        uuid = dg.config_group.removeprefix("Unnamed Stage ")
        UUID(uuid)  # Raises no error


class TestGetPipeweldStep:
    def test_no_name(self):
        # Arrange
        step = Step(
            name=None,
            script=Script(["echo foo"]),
        )

        # Act
        result = get_pipeweld_step(step)

        # Assert
        assert result == """{"script":["echo foo"]}"""

    def test_with_name(self):
        # Arrange
        step = Step(
            name="foo",
            script=Script(["echo foo"]),
        )

        # Act
        result = get_pipeweld_step(step)

        # Assert
        assert result == "foo"
