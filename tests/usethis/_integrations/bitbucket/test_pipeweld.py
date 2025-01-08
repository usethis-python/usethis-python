from pathlib import Path

import pytest

from usethis._integrations.bitbucket.errors import UnexpectedImportPipelineError
from usethis._integrations.bitbucket.pipeweld import (
    apply_pipeweld_instruction,
)
from usethis._integrations.bitbucket.schema import Script, Step
from usethis._pipeweld.ops import InsertSuccessor
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

    def test_insert_after(self, tmp_path: Path):
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
