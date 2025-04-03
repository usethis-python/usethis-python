from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

import ruamel.yaml
from ruamel.yaml.error import YAMLError
from ruamel.yaml.util import load_yaml_guess_indent

from usethis._console import info_print
from usethis._integrations.file.yaml.errors import InvalidYAMLError

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path
    from types import NoneType
    from typing import TypeAlias

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
    from ruamel.yaml.scalarstring import FoldedScalarString, LiteralScalarString
    from ruamel.yaml.timestamp import TimeStamp

    YAMLLiteral: TypeAlias = (
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


@dataclass
class YAMLDocument:
    """A dataclass to represent a YAML document in memory.

    Attributes:
        content: The content of the YAML document as a ruamel.yaml object.
    """

    content: YAMLLiteral


@contextmanager
def edit_yaml(
    yaml_path: Path,
    *,
    guess_indent: bool = True,
) -> Generator[YAMLDocument, None, None]:
    """A context manager to modify a YAML file in-place, with managed read and write."""
    with yaml_path.open(mode="r") as f:
        # Can't preserve quotes so don't keep the content.
        # Yes, it' not very efficient to load the content twice.
        try:
            content, sequence_ind, offset_ind = load_yaml_guess_indent(f)
        except YAMLError as err:
            msg = f"Error reading '{yaml_path}':\n{err}"

            if "mapping values are not allowed here" in str(err):
                info_print("Hint: You may have incorrect indentation the YAML file.")

            raise InvalidYAMLError(msg) from None
    if not guess_indent:
        sequence_ind = None
        offset_ind = None

    if sequence_ind is None:
        sequence_ind = 4
    if offset_ind is None:
        offset_ind = 2

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)
    yaml.preserve_quotes = True

    yaml_document = YAMLDocument(content=content)
    yield yaml_document

    yaml.dump(yaml_document.content, yaml_path)
