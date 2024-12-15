from pathlib import Path

import pytest

from usethis._integrations.bitbucket.anchor import ScriptItemAnchor
from usethis._integrations.bitbucket.io import edit_bitbucket_pipelines_yaml
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
    UnexpectedImportPipelineError,
    add_placeholder_step_in_default,
    add_step_in_default,
    get_defined_script_item_names_via_doc,
    get_steps_in_pipeline_item,
    remove_step_from_default,
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

    def test_add_same_step_twice(self, tmp_path: Path):
        # Arrange
        step = Step(
            name="Greeting",
            script=Script(
                [
                    ScriptItemAnchor(name="install-uv"),
                    "echo 'Hello, world!'",
                ]
            ),
        )

        with change_cwd(tmp_path):
            add_step_in_default(step)

            contents = (tmp_path / "bitbucket-pipelines.yml").read_text()

            # Act
            add_step_in_default(step)

        # Assert
        assert contents == (tmp_path / "bitbucket-pipelines.yml").read_text()

    def test_add_different_steps_sharing_same_script_step_anchor(self, tmp_path: Path):
        # Assert
        step = Step(
            name="Greeting",
            script=Script(
                [
                    ScriptItemAnchor(name="install-uv"),
                    "echo 'Hello, world!'",
                ]
            ),
        )
        other_step = Step(
            name="Farewell",
            script=Script(
                [
                    ScriptItemAnchor(name="install-uv"),
                    "echo 'Goodbye!'",
                ]
            ),
        )

        with change_cwd(tmp_path):
            # Act
            add_step_in_default(step)
            add_step_in_default(other_step)

            # Assert
            with edit_bitbucket_pipelines_yaml() as doc:
                names = get_defined_script_item_names_via_doc(doc=doc)
                assert len(names) == 1

    def test_order(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            # This step should be listed second
            add_step_in_default(
                Step(
                    name="Run tests with Python 3.12",
                    script=Script(["echo 'Running'"]),
                ),
            )
            # This one should come first
            add_step_in_default(
                Step(
                    name="Run pre-commit hooks",
                    script=Script(["echo 'Running'"]),
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
            name: Run pre-commit hooks
            script:
              - echo 'Running'
      - step:
            name: Run tests with Python 3.12
            script:
              - echo 'Running'
"""
        )
        # TODO so in terms of passing this test, I suspect the key is to revisit the
        # "precedent" logic used for hooks. The complication is that we have a notion
        # stages and parallel steps. Actually stages are conceptually very similar to
        # repos in pre-commit in the sense that it's a set of grouped steps in an
        # order. Ideally we can create some abstraction.
        # Parallel steps should probably be handled natively by the abstraction.
        # This deserves some kind of design, most likely.


class TestRemoveStepFromDefault:
    def test_remove_remove_one_step(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Greeting
            script: 
                - echo 'Hello, world!'
      - step:
            name: Farewell
            script:
                - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
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
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

    def test_no_file(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        assert not (tmp_path / "bitbucket-pipelines.yml").exists()

    def test_no_default_pipeline(self, tmp_path: Path):
        # Arrange
        txt = """\
image: atlassian/default-image:3
pipelines: {}
"""
        (tmp_path / "bitbucket-pipelines.yml").write_text(txt)

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").read_text() == txt

    def test_no_pipelines(self, tmp_path: Path):
        # Arrange
        txt = """\
image: atlassian/default-image:3
"""
        (tmp_path / "bitbucket-pipelines.yml").write_text(txt)

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
            )

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").read_text() == txt

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
            remove_step_from_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!'"]),
                )
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
                name: Greeting
                script:
                  - echo 'Hello, world!'
          - step:
                name: Farewell
                script:
                    - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
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
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

    def test_remove_single_parallel_step(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            - step:
                name: Greeting
                script:
                    - echo 'Hello, world!'
      - step:
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Greeting",
                    script=Script(["echo 'Hello, world!"]),
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
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

    def test_remove_leaving_single_parallel_step(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            - step:
                name: Greeting
                script:
                    - echo 'Hello, world!'
      - step:
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Farewell",
                    script=Script(["echo 'Goodbye!'"]),
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
      - parallel:
          - step:
                name: Greeting
                script:
                  - echo 'Hello, world!'
"""
        )

    def test_remove_step_leaving_placeholder(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Farewell",
                    script=Script(["echo 'Goodbye!'"]),
                )
            )

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
definitions:
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

    def test_remove_expanded_parallel_step(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            failfast: true
            steps:
              - step:
                    name: Greeting
                    script:
                        - echo 'Hello, world!'
              - step:
                    name: Farewell
                    script:
                      - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
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
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

    def test_remove_leaving_single_expanded_parallel_step(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - parallel:
            fail-fast: true
            steps:
              - step:
                    name: Greeting
                    script:
                      - echo 'Hello, world!'
      - step:
            name: Farewell
            script:
              - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Farewell",
                    script=Script(["echo 'Goodbye!'"]),
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
      - parallel:
            fail-fast: true
            steps:
              - step:
                    name: Greeting
                    script:
                      - echo 'Hello, world!'
"""
        )

    def test_stage_item(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Greeting
            script:
              - echo 'Hello, world!'
      - stage:
            name: Farewell
            steps:
              - step:
                    name: Farewell
                    script:
                      - echo 'Goodbye!'  
              - step:
                    name: Well wishes
                    script:
                      - echo 'Be well!'  
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Farewell",
                    script=Script(["echo 'Goodbye!'"]),
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
      - stage:
            name: Farewell
            steps:
              - step:
                    name: Well wishes
                    script:
                      - echo 'Be well!'
"""
        )

    def test_remove_stage_item_leaving_placeholder(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - stage:
            name: Farewell
            steps:
              - step:
                    name: Farewell
                    script:
                      - echo 'Goodbye!'
"""
        )

        # Act
        with change_cwd(tmp_path):
            remove_step_from_default(
                Step(
                    name="Farewell",
                    script=Script(["echo 'Goodbye!'"]),
                )
            )

        # Assert
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
definitions:
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
    EXPECTED_YML_SIMPLE_PLACEHOLDER = """\
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

    def test_contents(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            add_placeholder_step_in_default()

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        assert (
            tmp_path / "bitbucket-pipelines.yml"
        ).read_text() == self.EXPECTED_YML_SIMPLE_PLACEHOLDER

        out, _ = capfd.readouterr()
        # Keep these messages in sync with the ones used for pre-commit
        assert out == (
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding placeholder step to default pipeline in 'bitbucket-pipelines.yml'.\n"
            "☐ Remove the placeholder pipeline step in 'bitbucket-pipelines.yml'.\n"
            "☐ Replace it with your own pipeline steps.\n"
            "☐ Alternatively, use 'usethis tool' to add other tools and their steps.\n"
        )

    def test_idempotent(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            self.EXPECTED_YML_SIMPLE_PLACEHOLDER
        )

        # Act
        with change_cwd(tmp_path):
            add_placeholder_step_in_default()

        # Assert
        assert (
            tmp_path / "bitbucket-pipelines.yml"
        ).read_text() == self.EXPECTED_YML_SIMPLE_PLACEHOLDER


class TestGetDefinedScriptItemNames:
    def test_empty(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == []

    def test_no_definitions_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
"""
        )

        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == []

    def test_no_script_items_definitions_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
"""
        )

        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == []

    def test_no_anchor(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
definitions:
    script_items:
      - echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == [None]

    def test_anchor(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
definitions:
    script_items:
      - &say-hello |
        echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == ["say-hello"]

    def test_multiline_no_anchor(self, tmp_path: Path):
        # Arrange
        (tmp_path / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
definitions:
    script_items:
      - |
        echo 'Hello, world!'
"""
        )

        # Act
        with change_cwd(tmp_path), edit_bitbucket_pipelines_yaml() as doc:
            names = get_defined_script_item_names_via_doc(doc=doc)

        # Assert
        assert names == [None]
