from pathlib import Path

import pytest

from usethis._integrations.bitbucket.errors import UnexpectedImportPipelineError
from usethis._integrations.bitbucket.pipeweld import (
    apply_pipeweld_instruction,
)
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._pipeweld.containers import depgroup, parallel, series
from usethis._pipeweld.func import _get_instructions_for_insertion
from usethis._pipeweld.ops import InsertParallel, InsertSuccessor
from usethis._test import change_cwd


class TestApplyPipeweldInstruction:
    def test_add_to_brand_new_pipeline(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                new_step=Step(name="foo", script=Script(["echo foo"])),
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
        with change_cwd(tmp_path), pytest.raises(UnexpectedImportPipelineError):
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                new_step=Step(name="foo", script=Script(["echo foo"])),
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
        with change_cwd(tmp_path):
            apply_pipeweld_instruction(
                InsertSuccessor(step="foo", after=None),
                new_step=Step(name="foo", script=Script(["echo foo"])),
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
            with change_cwd(tmp_path):
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="bar"),
                    new_step=Step(name="foo", script=Script(["echo foo"])),
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
            with change_cwd(tmp_path):
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="qux"),
                    new_step=Step(name="foo", script=Script(["echo foo"])),
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
            with change_cwd(tmp_path):
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="qux"),
                    new_step=Step(name="foo", script=Script(["echo foo"])),
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
            with change_cwd(tmp_path):
                apply_pipeweld_instruction(
                    InsertSuccessor(step="foo", after="baz"),
                    new_step=Step(name="foo", script=Script(["echo foo"])),
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
            component = depgroup("A", series("B", "C"), category="x")
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
