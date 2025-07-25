from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import ValidationError
from ruamel.yaml.comments import CommentedMap

from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.file.yaml.io_ import edit_yaml
from usethis._integrations.pre_commit.schema import JsonSchemaForPreCommitConfigYaml
from usethis.errors import FileConfigError

if TYPE_CHECKING:
    from collections.abc import Generator

    from usethis._integrations.file.yaml.io_ import YAMLLiteral


class PreCommitConfigYAMLConfigError(FileConfigError):
    """Raised when there the 'bitbucket-pipelines.yml' file fails validation."""

    @property
    def name(self) -> str:
        """The name of the file that has a configuration error."""
        return ".pre-commit-config.yaml"


@dataclass
class PreCommitConfigYAMLDocument:
    """A dataclass to represent a pre-commit configuration YAML file in memory.

    Attributes:
        content: The content of the YAML document as a ruamel.yaml map (dict-like).
        model: A pydantic model containing a copy of the content.
    """

    content: CommentedMap
    model: JsonSchemaForPreCommitConfigYaml


@contextmanager
def edit_pre_commit_config_yaml() -> Generator[PreCommitConfigYAMLDocument, None, None]:
    """A context manager to modify '.pre-commit-config.yaml' in-place."""
    name = ".pre-commit-config.yaml"
    path = usethis_config.cpd() / name

    if not path.exists():
        tick_print(f"Writing '{name}'.")
        path.write_text("repos: []\n", encoding="utf-8")
        guess_indent = False
    else:
        guess_indent = True

    with edit_yaml(path, guess_indent=guess_indent) as doc:
        config = _validate_config(doc.content)
        yield PreCommitConfigYAMLDocument(content=doc.content, model=config)
        _validate_config(doc.content)


def _validate_config(ruamel_content: YAMLLiteral) -> JsonSchemaForPreCommitConfigYaml:
    if isinstance(ruamel_content, CommentedMap) and not ruamel_content:
        ruamel_content = CommentedMap({"repos": []})

    try:
        return JsonSchemaForPreCommitConfigYaml.model_validate(ruamel_content)
    except ValidationError as err:
        msg = f"Invalid '.pre-commit-config.yaml' file:\n{err}"
        raise PreCommitConfigYAMLConfigError(msg) from None
