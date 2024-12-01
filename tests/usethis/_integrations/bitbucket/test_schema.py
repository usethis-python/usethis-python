# TODO test that schema.json matches https://api.bitbucket.org/schemas/pipelines-configuration
# TODO we should use tjhe public API at https://www.schemastore.org/json/ to get the schema
# TODO Bump the 3.12 version in the command - also a test for bumping this.
# Corresponds to earliest supported python version.

from usethis._integrations.bitbucket.schema import Script, Step, Step2, StepBase


class TestStep2:
    def test_shared_parent(self):
        assert isinstance(Step2(script=Script(["hi"])), StepBase)
        assert isinstance(Step(script=Script(["hi"])), StepBase)

    def test_field_subset(self):
        assert set(Step2.model_fields.keys()) == set(Step.model_fields.keys())
