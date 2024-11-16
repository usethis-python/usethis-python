from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import NoneType
from typing import TypeVar

import ruamel.yaml
from ruamel.yaml.comments import (
    CommentedMap,
    CommentedOrderedMap,
    CommentedSeq,
    CommentedSet,
    TaggedScalar,
)
from ruamel.yaml.scalarbool import ScalarBoolean
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.scalarint import (
    BinaryInt,
    HexCapsInt,
    HexInt,
    OctalInt,
    ScalarInt,
)
from ruamel.yaml.scalarstring import (
    FoldedScalarString,
    LiteralScalarString,
)
from ruamel.yaml.timestamp import TimeStamp
from ruamel.yaml.util import load_yaml_guess_indent

T = TypeVar("T")


type YAMLLiteral = (
    NoneType
    | bool
    | float
    | int
    | str
    | BinaryInt
    | FoldedScalarString
    | HexInt
    | HexCapsInt
    | LiteralScalarString
    | OctalInt
    | ScalarBoolean
    | ScalarFloat
    | ScalarInt
    | TaggedScalar
    | TimeStamp
    | CommentedSeq
    | CommentedSet
    | CommentedOrderedMap
    | CommentedMap
)


def load_yaml(yaml_path: Path) -> YAMLLiteral:
    yaml = ruamel.yaml.YAML()
    with yaml_path.open(mode="r") as f:
        return yaml.load(f)


@dataclass
class YAMLDocument:
    """A dataclass to represent a YAML document in memory.

    Attributes:
        content: The content of the YAML document as a ruamel.yaml object.
    """

    content: YAMLLiteral


@contextmanager
def edit_yaml(yaml_path: Path) -> Generator[YAMLDocument, None, None]:
    """A context manager to modify a YAML file in-place, with managed read and write."""

    with yaml_path.open(mode="r") as f:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(f)

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)
    yaml.preserve_quotes = True

    yaml_document = YAMLDocument(content=content)
    yield yaml_document

    yaml.dump(yaml_document.content, yaml_path)
