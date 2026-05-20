"""YAML file manager for the pre-commit configuration."""

from __future__ import annotations

from pathlib import Path

import yamltrip
from pydantic import ValidationError
from typing_extensions import override

from usethis._file.yaml.io_ import YAMLDocument, YAMLFileManager
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.errors import PreCommitConfigYAMLConfigError
from usethis._integrations.pydantic.dump import fancy_model_dump


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
        content = doc.doc.get(default={})

        if isinstance(content, dict) and not content:
            content = {"repos": []}

        try:
            return schema.JsonSchemaForPreCommitConfigYaml.model_validate(content)
        except ValidationError as err:
            msg = f"Invalid '.pre-commit-config.yaml' file:\n{err}"
            raise PreCommitConfigYAMLConfigError(msg) from None

    def commit_model(self, model: schema.JsonSchemaForPreCommitConfigYaml) -> None:
        """Sync the YAML file's repos list to match the model."""
        repos_list = [
            fancy_model_dump(r, reference={}, order_by_cls={}) for r in model.repos
        ]
        doc = self.get().doc
        try:
            doc = doc.sync("repos", value=repos_list)
        except yamltrip.PatchError:
            # Flow sequence (e.g. `repos: []`) — fall back to full replacement.
            doc = doc.upsert("repos", value=repos_list)
        self.commit(YAMLDocument(doc=doc))
