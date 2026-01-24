import os
from pathlib import Path

import pytest
import requests
from requests.exceptions import RequestException

from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.requires_python import (
    get_requires_python,
)
from usethis._integrations.ci.bitbucket import schema
from usethis._test import change_cwd, is_offline


class TestStep2:
    def test_shared_parent(self):
        assert isinstance(schema.Step2(script=schema.Script(["hi"])), schema.StepBase)
        assert isinstance(schema.Step(script=schema.Script(["hi"])), schema.StepBase)

    def test_field_subset(self):
        assert set(schema.Step2.model_fields.keys()) == set(
            schema.Step.model_fields.keys()
        )


class TestSchemaJSON:
    def test_matches_schema_store(self):
        if is_offline():
            pytest.skip("Cannot fetch JSON schema when offline")

        local_schema_json = (Path(__file__).parent / "schema.json").read_text()
        try:
            online_schema_json = requests.get(
                "https://api.bitbucket.org/schemas/pipelines-configuration", timeout=5
            ).text
        except RequestException as err:
            if os.getenv("CI"):
                pytest.skip(
                    "Failed to fetch JSON schema (connection issues); skipping test"
                )
            raise err

        # Compare the JSON
        # TIP: go into debug mode to copy-and-paste print(online_schema_json)
        # into updated schema.json
        assert local_schema_json == online_schema_json

    def test_target_python_version(self, usethis_dev_dir: Path):
        # If this test fails, we should bump the version in the command in schema.py
        with change_cwd(usethis_dev_dir), PyprojectTOMLManager():
            assert get_requires_python() == ">=3.10"
