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
from ruamel.yaml.scalarint import BinaryInt, HexCapsInt, HexInt, OctalInt, ScalarInt
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
