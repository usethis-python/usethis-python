from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError
from ruamel.yaml.comments import CommentedMap

from usethis._integrations.file.yaml.io_ import YAMLFileManager
from usethis._integrations.file.yaml.update import update_ruamel_yaml_map
from usethis._integrations.pre_commit.errors import PreCommitConfigYAMLConfigError
from usethis._integrations.pre_commit.schema import JsonSchemaForPreCommitConfigYaml
from usethis._integrations.pydantic.dump import fancy_model_dump

if TYPE_CHECKING:
    from pydantic import BaseModel

    from usethis._integrations.pydantic.dump import ModelRepresentation

ORDER_BY_CLS: dict[type[BaseModel], list[str]] = {}


class PreCommitConfigYAMLManager(YAMLFileManager):
    """Class to manage the .pre-commit-config.yaml file."""

    @property
    def relative_path(self) -> Path:
        return Path(".pre-commit-config.yaml")

    def model_validate(self) -> JsonSchemaForPreCommitConfigYaml:
        """Validate the current document content against the JSON schema.

        Returns:
            Validated pydantic model.

        Raises:
            PreCommitConfigYAMLConfigError: If validation fails.
        """
        doc = self.get()
        ruamel_content = doc.content

        if isinstance(ruamel_content, CommentedMap) and not ruamel_content:
            ruamel_content = CommentedMap({"repos": []})

        try:
            return JsonSchemaForPreCommitConfigYaml.model_validate(ruamel_content)
        except ValidationError as err:
            msg = f"Invalid '.pre-commit-config.yaml' file:\n{err}"
            raise PreCommitConfigYAMLConfigError(msg) from None

    def commit_model(self, model: JsonSchemaForPreCommitConfigYaml) -> None:
        doc = self.get()
        dump = _pre_commit_fancy_dump(model, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)
        self.model_validate()
        self.commit(doc)


def _pre_commit_fancy_dump(
    config: JsonSchemaForPreCommitConfigYaml, *, reference: ModelRepresentation
) -> dict[str, ModelRepresentation]:
    dump = fancy_model_dump(config, reference=reference, order_by_cls=ORDER_BY_CLS)

    if not isinstance(dump, dict):
        msg = (
            f"Invalid '{type(config)}' representation when dumping; expected dict, got "
            f"'{type(dump)}'."
        )
        raise TypeError(msg)

    return dump
