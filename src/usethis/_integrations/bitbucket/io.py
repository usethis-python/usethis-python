from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError
from ruamel.yaml.comments import CommentedMap

from usethis._console import tick_print
from usethis._integrations.bitbucket.schema import PipelinesConfiguration
from usethis._integrations.yaml.io import YAMLLiteral, edit_yaml


class BitbucketPipelinesYAMLConfigError(Exception):
    """Raised when there the 'bitbucket-pipelines.yml' file fails validation."""


@dataclass
class BitbucketPipelinesYAMLDocument:
    """A dataclass to represent a Bitbucket Pipelines configuration YAML file in memory.

    Attributes:
        content: The content of the YAML document as a ruamel.yaml map (dict-like).
        model: A pydantic model containing a copy of the content.
    """

    content: CommentedMap
    model: PipelinesConfiguration


@contextmanager
def edit_bitbucket_pipelines_yaml() -> (
    Generator[BitbucketPipelinesYAMLDocument, None, None]
):
    """A context manager to modify 'bitbucket-pipelines.yml' in-place."""
    name = "bitbucket-pipelines.yml"
    path = Path.cwd() / name

    if not path.exists():
        # TODO test this message. Also test the validation passes - it should
        # but we should test it (maybe we already do?). If it is valid, we should
        # add a comment to to path.touch() line.
        tick_print(f"Writing '{name}'.")
        path.touch()

    with edit_yaml(path) as doc:
        config = _validate_config(doc.content)
        yield BitbucketPipelinesYAMLDocument(content=doc.content, model=config)
        config = _validate_config(doc.content)


def _validate_config(ruamel_content: YAMLLiteral) -> PipelinesConfiguration:
    try:
        return PipelinesConfiguration.model_validate(ruamel_content)
    except ValidationError as err:
        msg = f"Invalid 'bitbucket-pipelines.yml' file:\n{err}"
        raise BitbucketPipelinesYAMLConfigError(msg) from None
