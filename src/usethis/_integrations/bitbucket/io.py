from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from usethis._integrations.bitbucket.pipeline import PipelinesConfiguration
from usethis._integrations.yaml.io import (
    YAMLDocument,
    YAMLLiteral,
    edit_yaml,
    load_yaml,
)


class BitbucketPipelinesYAMLConfigError(Exception):
    """Raised when there the 'bitbucket-pipelines.yml' file fails validation."""


@dataclass
class BitbucketPipelinesYAMLDocument(YAMLDocument):
    model: PipelinesConfiguration


def read_bitbucket_pipelines_yaml() -> PipelinesConfiguration:
    path = Path.cwd() / "bitbucket-pipelines.yml"

    ruamel_content = load_yaml(path)

    return _validate_config(ruamel_content)


@contextmanager
def edit_bitbucket_pipelines_yaml() -> (
    Generator[BitbucketPipelinesYAMLDocument, None, None]
):
    """A context manager to modify 'bitbucket-pipelines.yml' in-place."""
    path = Path.cwd() / "bitbucket-pipelines.yml"

    if not path.exists():
        path.touch()

    with edit_yaml(path) as doc:
        config = _validate_config(doc.content)

        yield BitbucketPipelinesYAMLDocument(content=doc.content, model=config)


def _validate_config(ruamel_content: YAMLLiteral) -> PipelinesConfiguration:
    try:
        return PipelinesConfiguration.model_validate(ruamel_content)
    except ValidationError as err:
        msg = f"Invalid 'bitbucket-pipelines.yml' file:\n{err}"
        raise BitbucketPipelinesYAMLConfigError(msg) from None
