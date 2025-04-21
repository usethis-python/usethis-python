from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError

from usethis._console import tick_print
from usethis._integrations.ci.bitbucket.schema import PipelinesConfiguration
from usethis._integrations.file.yaml.io_ import edit_yaml

if TYPE_CHECKING:
    from collections.abc import Generator

    from ruamel.yaml.comments import CommentedMap

    from usethis._integrations.file.yaml.io_ import YAMLLiteral


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
def edit_bitbucket_pipelines_yaml() -> Generator[
    BitbucketPipelinesYAMLDocument, None, None
]:
    """A context manager to modify 'bitbucket-pipelines.yml' in-place."""
    name = "bitbucket-pipelines.yml"
    path = Path.cwd() / name

    if not path.exists():
        tick_print(f"Writing '{name}'.")
        path.write_text("image: atlassian/default-image:3", encoding="utf-8")
        guess_indent = False
    else:
        guess_indent = _has_indentation(path)

    with edit_yaml(path, guess_indent=guess_indent) as doc:
        config = _validate_config(doc.content)
        yield BitbucketPipelinesYAMLDocument(content=doc.content, model=config)
        _validate_config(doc.content)


def _validate_config(ruamel_content: YAMLLiteral) -> PipelinesConfiguration:
    try:
        return PipelinesConfiguration.model_validate(ruamel_content)
    except ValidationError as err:
        msg = f"Invalid 'bitbucket-pipelines.yml' file:\n{err}"
        raise BitbucketPipelinesYAMLConfigError(msg) from None


def _has_indentation(path: Path) -> bool:
    lines = path.read_text().splitlines()
    return any(line.startswith(" ") or line.startswith("\t") for line in lines)
