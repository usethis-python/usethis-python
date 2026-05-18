"""YAML file manager for the pre-commit configuration."""

from __future__ import annotations

from pathlib import Path

import yamltrip
from pydantic import ValidationError
from typing_extensions import override

from usethis._file.yaml.io_ import YAMLFileManager
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.errors import PreCommitConfigYAMLConfigError


class PreCommitConfigYAMLManager(YAMLFileManager):
    """Class to manage the .pre-commit-config.yaml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path(".pre-commit-config.yaml")

    def model_validate(self) -> schema.JsonSchemaForPreCommitConfigYaml:
        """Validate the current document content against the JSON schema.

        Returns:
            Validated pydantic model.

        Raises:
            PreCommitConfigYAMLConfigError: If validation fails.
        """
        doc = self.get()
        try:
            content = doc.doc.root
        except yamltrip.QueryError:
            content = {}

        if isinstance(content, dict) and not content:
            content = {"repos": []}

        try:
            return schema.JsonSchemaForPreCommitConfigYaml.model_validate(content)
        except ValidationError as err:
            msg = f"Invalid '.pre-commit-config.yaml' file:\n{err}"
            raise PreCommitConfigYAMLConfigError(msg) from None
